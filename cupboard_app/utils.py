import os
import json

import jwt
import requests
from django.contrib.auth import authenticate

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')


def jwt_get_username_from_payload_handler(payload):
    """
    Maps the sub field from the access_token to the username.
    The authenticate method creates a remote user and returns
    a User object for the username.

    Args:
        payload: body of the API request.

    Returns:
        Remote user object for the specified username.
    """
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def jwt_decode_token(token):
    """
    Fetches the JWKS from Auth0 account to verify and decode the
    incoming Access Token.

    Args:
        token: The access token.

    Returns:
        Decoded access token.
    """
    header = jwt.get_unverified_header(token)
    jwks = requests.get('https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN)).json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = 'https://{}/'.format(AUTH0_DOMAIN)
    return jwt.decode(
        token,
        public_key,
        audience=AUTH0_API_IDENTIFIER,
        issuer=issuer,
        algorithms=['RS256']
    )
