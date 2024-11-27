import os
from time import strftime, localtime
from urllib.parse import quote_plus, urlencode

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
from rest_framework_simplejwt.backends import TokenBackend

from cupboard_app.exceptions import MissingInformation
from cupboard_app.models import Message
from cupboard_app.serializers import MessageSerializer
from cupboard_app.queries import (
    create_user,
    add_default_user_lists
)
from utils.api_helper import (
    get_auth_username_from_payload,
    get_auth_email_from_payload,
    EMAIL_CLAIM
) 


AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')
AUTH0_BACKEND_CLIENT_ID = os.getenv('AUTH0_BACKEND_CLIENT_ID')
AUTH0_BACKEND_CLIENT_SECRET = os.getenv('AUTH0_BACKEND_CLIENT_SECRET')

TOKEN_TIMESTAMP = '%Y-%m-%d %H:%M:%S'


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


def login_callback(request: Request) -> HttpResponseRedirect:
    """
    Callback from the login.
    Creates a user if user does not exist in the database.
    Saves the access token and the refresh tokens in the database.
    Redirects to the login endpoint.
    """
    token = login_oauth.auth0.authorize_access_token(request)

    access_token = token.get('access_token')
    refresh_token = token.get('refresh_token')
    expire_time = token.get('expires_at')
    issued_time = token.get('expires_at') - token.get('expires_in')

    payload = AccessToken(access_token)
    username = get_auth_username_from_payload(payload=payload)
    email = get_auth_email_from_payload(payload=payload)

    # Check if the user exists in the database, if not create the user
    # and create default lists for the user
    if email and username:
        create_user(username=username, email=email)
        add_default_user_lists(username=username)

    token = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': token.get('id_token'),
        'issued_time': strftime(TOKEN_TIMESTAMP, localtime(issued_time)),
        'expire_time': strftime(TOKEN_TIMESTAMP, localtime(expire_time)),
        'user_info': token.get('userinfo')
    }

    request.session['user'] = token

    return redirect(request.build_absolute_uri(reverse('login')))


def logout_callback(request: Request) -> HttpResponseRedirect:
    """
    Callback from the logout.
    Redirects to the logout endpoint.
    """
    return redirect(request.build_absolute_uri(reverse('logout')))


@extend_schema(tags=['Authentication'])
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=None,
        responses= {
            200: inline_serializer(
                name='Login',
                fields={
                    'token': serializers.JSONField(),
                    'user_info': serializers.JSONField()
                }
            )
        },
        examples=[
            OpenApiExample(
                name='Login successful',
                value={
                    'token': {
                        'access_token': 'very_long_jwt_token',
                        'refresh_token': 'refresh_token',
                        'expire_time': '2024-11-17 01:49:09',
                        'issued_time': '2024-11-16 01:49:09',
                        'id_token': 'very_long_jwt_token'
                    },
                    'user_info': {
                        'nickname': 'teacup.backend',
                        'name': 'teacup.backend@gmail.com',
                        'picture': 'image_url',
                        'updated_at': '2024-11-16T07:49:07.640Z',
                        'email': 'teacup.backend@gmail.com',
                        'email_verified': True,
                        'iss': 'https://dev-cupboard.ca.auth0.com/',
                        'aud': 'audience_string',
                        'iat': 1731743349,
                        'exp': 1731779349,
                        'sub': 'auth0|982734jhe98whjhw8',
                        'sid': 'session_id',
                        'nonce': 'random_value'
                    }
                },
                status_codes=[200],
                response_only=True
            )
        ]
    )
    def get(self, request: Request) -> Response | HttpResponseRedirect:
        """
        Redirects to the Auth0 universal login for user to enter credentials.
        The user is then sent the access token, refresh token, issued time and
        expire time.
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
    text = 'Logout successful. Login again using the login endpoint.'

    @extend_schema(
        request=None,
        responses=MessageSerializer,
        examples=[
            OpenApiExample(name='Success', value={'message': text}, status_codes=[200])
        ]
    )
    def get(self, request: Request) -> Response | HttpResponseRedirect:
        """
        Logs out the user from Auth0.
        """
        if request.session.get('user'):
            request.session.clear()
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
            message = Message(message=self.text)
            serializer = MessageSerializer(message)
            result = Response(serializer.data, status=200)

        return result


def set_session(request: Request, token_info: str):
    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')
    id_token = token_info.get('id_token')

    payload = AccessToken(access_token)
    issued_time = payload.get('iat')
    expire_time = payload.get('exp')

    new_session = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': id_token,
        'issued_time': strftime(TOKEN_TIMESTAMP, localtime(issued_time)),
        'expire_time': strftime(TOKEN_TIMESTAMP, localtime(expire_time)),
        'user_info': request.session.get('user').get('user_info')
    }

    request.session['user'] = new_session

    '''
    print(f'Bearer {access_token}')
    try:
        response = requests.get(
            f'https://{AUTH0_DOMAIN}/userinfo',
            headers = {'Authorization': f'Bearer {access_token}'},
            data={'scope': 'openid', 'audience': AUTH0_API_IDENTIFIER}
        )
        print(response.json())
    except Exception as e:
        print(e)

    try:
        token_backend = TokenBackend(
            algorithm='RS256',
            audience=AUTH0_API_IDENTIFIER,
            issuer=f'https://{AUTH0_DOMAIN}/',
            jwk_url=f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
        )
        token_backend.decode(token=id_token)
    except Exception as e:
        print(e)
    '''


@extend_schema(tags=['Authentication'])
class RefreshAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response | HttpResponseRedirect:
        """
        Refreshes the access token for the user from Auth0.
        """
        session = request.session.get('user')
        refresh_token = session.get('refresh_token')

        if refresh_token:
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
                print('Failed operation')
        else:
            MissingInformation('Refresh Token missing.')

        return result
