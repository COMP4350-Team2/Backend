import os
from time import strftime, localtime
from urllib.parse import quote_plus, urlencode

import jwt
import requests
from authlib.integrations.django_client import OAuth
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
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


# Auth0 Client setup
login_oauth = OAuth()
login_oauth.register(
    'auth0',
    client_id=AUTH0_BACKEND_CLIENT_ID,
    client_secret=AUTH0_BACKEND_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid profile email offline_access',
    },
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
)


def set_session(request: Request, token_info: str):
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


def login_callback(request: Request) -> HttpResponseRedirect:
    """
    Callback from the login. Creates a user if user does not exist in the database.
    Then redirects to the login endpoint.

    Args:
        request: The current request

    Returns:
        Redirects back to the login endpoint with session set if no errors occurred.
    """
    token = login_oauth.auth0.authorize_access_token(request)

    set_session(request=request, token_info=token)
    session = request.session.get('user')
    initialize_user_in_db(session=session)

    return redirect(request.build_absolute_uri(reverse('login')))


def logout_callback(request: Request) -> HttpResponseRedirect:
    """
    Callback from the logout. Clears the session and redirects
    to the logout endpoint.

    Args:
        request: The current request

    Returns:
        Redirects back to the logout endpoint with session cleared if no errors occurred.
    """
    request.session.clear()
    return redirect(request.build_absolute_uri(reverse('logout')))


@extend_schema(tags=['Authentication'])
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=None,
        responses={
            200: SessionSerializer
        },
        examples=[session_example]
    )
    def get(self, request: Request) -> Response | HttpResponseRedirect:
        """
        Redirects to the Auth0 universal login for user to enter credentials if
        session is not set. Returns the access token, refresh token, id token,
        and user info.
        """
        session = request.session.get('user')
        if session:
            result = Response(session, status=200)
        else:
            result = login_oauth.auth0.authorize_redirect(
                request,
                request.build_absolute_uri(reverse('login_callback')),
                audience=AUTH0_API_IDENTIFIER
            )

        return result


@extend_schema(tags=['Authentication'])
class LogoutAPIView(APIView):
    permission_classes = [AllowAny]
    LOGOUT_MSG = 'Logout successful. Login again using the login endpoint.'

    @extend_schema(
        request=None,
        responses={
            200: MessageSerializer
        },
        examples=[
            OpenApiExample(
                name='Logout Success',
                value={'message': LOGOUT_MSG},
                status_codes=[200],
                response_only=True
            )
        ]
    )
    def get(self, request: Request) -> Response | HttpResponseRedirect:
        """
        Logs out the user from Auth0 and clears the session.
        """
        if request.session.get('user'):
            result = redirect(
                f'https://{AUTH0_DOMAIN}/v2/logout?'
                + urlencode(
                    {
                        'returnTo': request.build_absolute_uri(reverse('logout_callback')),
                        'client_id': AUTH0_BACKEND_CLIENT_ID,
                    },
                    quote_via=quote_plus,
                )
            )
        else:
            message = Message(message=self.LOGOUT_MSG)
            serializer = MessageSerializer(message)
            result = Response(serializer.data, status=200)

        return result


@extend_schema(tags=['Authentication'])
class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]
    MISSING_REFRESH_TOKEN = 'Refresh token is missing.'

    @extend_schema(
        request=None,
        responses={
            200: SessionSerializer,
            400: MessageSerializer
        },
        examples=[
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
        session = request.session.get('user')
        refresh_token = session.get('refresh_token')

        if refresh_token:
            try:
                response = requests.post(
                    f'https://{AUTH0_DOMAIN}/oauth/token',
                    headers={'content-type': 'application/x-www-form-urlencoded'},
                    data={
                        'grant_type': 'refresh_token',
                        'client_id': AUTH0_BACKEND_CLIENT_ID,
                        'client_secret': AUTH0_BACKEND_CLIENT_SECRET,
                        'audience': AUTH0_API_IDENTIFIER,
                        'refresh_token': refresh_token
                    }
                )

                if response.status_code == 200:
                    set_session(request=request, token_info=response.json())
                    session = request.session.get('user')
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
            name='CLILoginRequestSerializer',
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
                    set_session(request=request, token_info=response.json())
                    session = request.session.get('user')
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
    permission_classes = [AllowAny]
    LOGOUT_MSG = 'Logout successful. Login again using the login endpoint.'

    @extend_schema(
        request=None,
        responses={
            200: MessageSerializer
        },
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
