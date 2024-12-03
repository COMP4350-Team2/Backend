import os
from time import strftime, localtime

import jwt
import requests
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample
)
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from cupboard_app.exceptions import (
    FailedOperation,
    MissingInformation
)
from cupboard_app.models import Message
from cupboard_app.serializers import (
    MessageSerializer,
    SessionSerializer
)
from cupboard_app.queries import (
    create_user,
    add_default_user_lists
)
from utils.api_helper import (
    get_auth_username_from_payload,
    get_auth_email_from_payload
)

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')
AUTH0_BACKEND_CLIENT_ID = os.getenv('AUTH0_BACKEND_CLIENT_ID')
AUTH0_BACKEND_CLIENT_SECRET = os.getenv('AUTH0_BACKEND_CLIENT_SECRET')
AUTH0_DESKTOP_CLIENT_ID = os.getenv('AUTH0_DESKTOP_CLIENT_ID')
AUTH0_DESKTOP_CLIENT_SECRET = os.getenv('AUTH0_DESKTOP_CLIENT_SECRET')
TOKEN_TIMESTAMP = '%Y-%m-%d %H:%M:%S'

session_example = OpenApiExample(
    name='Login Success',
    value={
        'access_token': 'very_long_jwt_token',
        'refresh_token': 'refresh_token',
        'id_token': 'very_long_jwt_token',
        'issued_time': '2024-11-16 01:49:09',
        'expire_time': '2024-11-17 01:49:09',
        'user_info': {
            'nickname': 'teacup.backend',
            'name': 'cupboard@teacup.ca',
            'picture': 'image_url',
            'updated_at': '2024-11-16T07:49:07.640Z',
            'email': 'cupboard@teacup.ca',
            'email_verified': True,
            'iss': 'issuer_string',
            'aud': 'audience_string',
            'iat': 1731743349,
            'exp': 1731779349,
            'sub': 'auth0|fake_user_string',
            'sid': 'session_id'
        }
    },
    status_codes=[200],
    response_only=True
)


def set_session(request: Request, token_info: str) -> dict:
    '''
    Sets the session for the user using the returned token information
    from Auth0.

    Args:
        request: The current request
        token_info: The returned token information from Auth0
    '''
    # Get all the tokens
    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')
    id_token = token_info.get('id_token')

    # Get all the issued and expire time from the decoded access token
    payload = AccessToken(access_token)
    issued_time = payload.get('iat')
    expire_time = payload.get('exp')

    # Decode the id_token for user information
    user_info = jwt.decode(id_token, options={"verify_signature": False})

    # Create session dictionary and save to session
    new_session = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': id_token,
        'issued_time': strftime(TOKEN_TIMESTAMP, localtime(issued_time)),
        'expire_time': strftime(TOKEN_TIMESTAMP, localtime(expire_time)),
        'user_info': user_info
    }
    request.session['user'] = new_session

    return new_session


def initialize_user_in_db(session: dict):
    if session:
        payload = AccessToken(session.get('access_token'))
        username = get_auth_username_from_payload(payload=payload)
        email = get_auth_email_from_payload(payload=payload)

        # Check if the user exists in the database, if not create the user
        # and create default lists for the user
        if username and email:
            create_user(username=username, email=email)
            add_default_user_lists(username=username)


@extend_schema(tags=['Authentication'])
class RefreshTokenAPIView(APIView):
    MISSING_REFRESH_TOKEN = 'Client ID or Refresh token is missing.'

    @extend_schema(
        request=inline_serializer(
            name='RefreshTokenRequestSerializer',
            fields={
                'client_id': serializers.CharField(),
                'client_secret': serializers.CharField(required=False),
                'refresh_token': serializers.CharField()
            }
        ),
        responses={
            200: SessionSerializer,
            400: MessageSerializer
        },
        examples=[
            OpenApiExample(
                name='All Body Parameters',
                value={
                    'client_id': 'skjehfgef98732984hjkfse',
                    'client_secret': 'whdkjsjkabuie32984hiou298qhdkj93782hiudh',
                    'refresh_token': 'iudoue98yu3ugifhkjo823iuygugik'
                },
                request_only=True
            ),
            OpenApiExample(
                name='Without Client Secret',
                value={
                    'client_id': 'skjehfgef98732984hjkfse',
                    'refresh_token': 'iudoue98yu3ugifhkjo823iuygugik'
                },
                request_only=True
            ),
            session_example,
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_REFRESH_TOKEN},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def post(self, request: Request) -> Response:
        """
        Refreshes the access token for the user from Auth0.
        """
        body = request.data
        if (
            body.get('client_id', None)
            and body.get('refresh_token', None)
        ):
            client_id = body['client_id']
            refresh_token = body['refresh_token']

            # Check for client secret. Desktop does not have client secret in the frontend
            if body.get('client_secret', None):
                client_secret = body['client_secret']
            elif client_id == AUTH0_DESKTOP_CLIENT_ID:
                client_secret = AUTH0_DESKTOP_CLIENT_SECRET
            elif client_id == AUTH0_BACKEND_CLIENT_ID:
                client_secret = AUTH0_BACKEND_CLIENT_SECRET

            try:
                response = requests.post(
                    f'https://{AUTH0_DOMAIN}/oauth/token',
                    headers={'content-type': 'application/x-www-form-urlencoded'},
                    data={
                        'grant_type': 'refresh_token',
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'audience': AUTH0_API_IDENTIFIER,
                        'refresh_token': refresh_token
                    }
                )

                if response.status_code == 200:
                    session = set_session(request=request, token_info=response.json())
                    result = Response(session, status=200)
                else:
                    raise FailedOperation(response.json())
            except Exception as e:
                raise FailedOperation(str(e))
        else:
            raise MissingInformation(self.MISSING_REFRESH_TOKEN)

        return result


@extend_schema(tags=['Authentication'])
class CLILoginAPIView(APIView):
    permission_classes = [AllowAny]
    MISSING_CREDENTIALS = 'Username or password missing.'

    @extend_schema(
        request=inline_serializer(
            name='LoginRequestSerializer',
            fields={
                'username': serializers.CharField(),
                'password': serializers.CharField()
            }
        ),
        responses={
            200: SessionSerializer,
            400: MessageSerializer
        },
        examples=[
            OpenApiExample(
                name='Login Credentials',
                value={
                    'username': 'cupboard@teacup.ca',
                    'password': 'Fake_password'
                },
                request_only=True
            ),
            session_example,
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_CREDENTIALS},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def post(self, request: Request) -> Response:
        """
        Logs in user using Auth0 if session is not set.
        Returns the access token, refresh token, id token, and user info.
        """
        session = request.session.get('user', None)
        body = request.data

        if session:
            result = Response(session, status=200)
        elif (
            body.get('username', None)
            and body.get('password', None)
        ):
            try:
                response = requests.post(
                    f'https://{AUTH0_DOMAIN}/oauth/token',
                    headers={'content-type': 'application/x-www-form-urlencoded'},
                    data={
                        'grant_type': 'password',
                        'client_id': AUTH0_BACKEND_CLIENT_ID,
                        'client_secret': AUTH0_BACKEND_CLIENT_SECRET,
                        'audience': AUTH0_API_IDENTIFIER,
                        'scope': 'openid profile email offline_access',
                        'username': body['username'],
                        'password': body['password']
                    }
                )

                if response.status_code == 200:
                    session = set_session(request=request, token_info=response.json())
                    initialize_user_in_db(session=session)
                    result = Response(session, status=200)
                else:
                    raise FailedOperation(response.json())
            except Exception as e:
                raise FailedOperation(str(e))
        else:
            raise MissingInformation(self.MISSING_CREDENTIALS)

        return result


@extend_schema(tags=['Authentication'])
class CLILogoutAPIView(APIView):
    LOGOUT_MSG = 'Logout successful. Login again using the login endpoint.'

    @extend_schema(
        request=None,
        responses={200: MessageSerializer},
        examples=[
            OpenApiExample(
                name='Logout Success',
                value={'message': LOGOUT_MSG},
                status_codes=[200],
                response_only=True
            )
        ]
    )
    def post(self, request: Request) -> Response:
        """
        Logs out the user from Auth0 and clears the session.
        """
        request.session.clear()
        message = Message(message=self.LOGOUT_MSG)
        serializer = MessageSerializer(message)

        return Response(serializer.data, status=200)
