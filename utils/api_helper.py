from django.contrib.auth import authenticate
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import AccessToken

EMAIL_CLAIM = 'https://cupboard-teacup.com/email'


def get_auth_access_token_from_header(request: Request) -> str:
    """
    Obtains the Access Token from the Authorization Header

    Args:
        request: The rest framework Request object

    Returns:
        The access token from the request.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', None)
    parts = auth.split()
    token = parts[1]

    return token


def get_auth_username_from_payload(request: Request = None, payload: AccessToken = None) -> str:
    """
    Maps the sub field from the access_token to the username.
    The authenticate method creates a remote user and returns
    a User object for the username.

    Args:
        request: The rest framework Request object
        payload: The simple_jwt access token object

    Returns:
        Username string for the specified user.
    """
    if request:
        username = request.auth.get('sub').replace('|', '.')
    elif payload:
        username = payload['sub'].replace('|', '.')
    else:
        raise ValueError('Missing sub field in access token.')
    authenticate(remote_user=username)
    return username


def get_auth_email_from_payload(request: Request = None, payload: AccessToken = None) -> str:
    """
    Extracts the email field field from the access_token.

    Args:
        request: The rest framework Request object
        payload: The simple_jwt access token object

    Returns:
        Email string for the specified user.
    """
    if request:
        email = request.auth.get(EMAIL_CLAIM)
    elif payload:
        email = payload[EMAIL_CLAIM]
    else:
        raise ValueError(f'Missing {EMAIL_CLAIM} field in access token.')

    return email
