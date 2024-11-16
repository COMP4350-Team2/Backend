import os
from urllib.parse import quote_plus, urlencode

from authlib.integrations.django_client import OAuth
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
)
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from cupboard_app.models import Message
from cupboard_app.serializers import MessageSerializer
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


# Auth0 Client setup
oauth = OAuth()
oauth.register(
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
    token = oauth.auth0.authorize_access_token(request)
    request.session['user'] = token

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

    # Save the access token and the refresh token for the user in the db

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
    text = 'Login successful.'

    @extend_schema(
        request=None,
        responses=MessageSerializer,
        examples=[
            OpenApiExample(name='Success', value={'message': text}, status_codes=[200])
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
            message = Message(message=self.text)
            serializer = MessageSerializer(message)
            result = Response(serializer.data, status=200)
        else:
            result = oauth.auth0.authorize_redirect(
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
            # Remove the access token and refresh token from the database
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
