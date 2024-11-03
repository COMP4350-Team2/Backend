from django.contrib.auth import authenticate
from rest_framework.request import Request


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


def get_auth_username_from_payload(request: Request) -> str:
    """
    Maps the sub field from the access_token to the username.
    The authenticate method creates a remote user and returns
    a User object for the username.

    Args:
        request: The rest framework Request object

    Returns:
        Username string for the specified user.
    """
    username = request.auth.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def get_auth_email_from_payload(request: Request) -> str:
    """
    Extracts the email field field from the access_token.

    Args:
        request: The rest framework Request object

    Returns:
        Email string for the specified user.
    """
    email = request.auth.get('https://cupboard-teacup.com/email')
    return email
