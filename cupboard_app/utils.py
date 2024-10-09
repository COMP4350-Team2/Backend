import os
import json

import jwt
import requests
from django.contrib.auth import authenticate
from rest_framework.request import Request

DEV_LAYER = os.getenv('DEV_LAYER')
TEST_RUN = os.getenv('TEST_RUN')
TEST_KEY = os.getenv('TEST_KEY')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')


def get_auth_access_token_from_header(request: Request) -> str:
    """
    Obtains the Access Token from the Authorization Header

    Args:
        request: The rest framework Request object

    Returns:
        The access token from the request.
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


def decode_auth_access_token(token: str) -> dict:
    """
    Fetches the JWKS from Auth0 account to verify and decode the
    incoming Access Token.

    Args:
        token: The access token.

    Returns:
        Decoded access token in the form of dictionary.
    """
    result = {}
    header = jwt.get_unverified_header(token)
    issuer = 'https://{}/'.format(AUTH0_DOMAIN)

    if DEV_LAYER == 'mock' or TEST_RUN == 'true':
        result = jwt.decode(
            token,
            TEST_KEY,
            audience=AUTH0_API_IDENTIFIER,
            issuer=issuer,
            algorithms=['HS256']
        )
    else:
        jwks = requests.get('https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN)).json()

        # Find public key
        public_key = None
        for jwk in jwks['keys']:
            if jwk['kid'] == header['kid']:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

        if public_key is None:
            raise Exception('Public key not found.')

        result = jwt.decode(
            token,
            public_key,
            audience=AUTH0_API_IDENTIFIER,
            issuer=issuer,
            algorithms=['RS256']
        )
    return result


def get_auth_username_from_payload(payload: dict) -> str:
    """
    Maps the sub field from the access_token to the username.
    The authenticate method creates a remote user and returns
    a User object for the username.

    Args:
        payload: dictionary of the payload resulting from
                 decoding the auth0 access token

    Returns:
        Username string for the specified username.
    """
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username
