import os
import json
import http.client

import jwt
import requests
from django.contrib.auth import authenticate

DEV_LAYER = os.getenv('DEV_LAYER')
PORT = os.getenv('DJANGO_PORT')
TEST_RUN = os.getenv('TEST_RUN')
TEST_KEY = os.getenv('TEST_KEY')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')
AUTH0_API_AUDIENCE = os.getenv('AUTH0_API_AUDIENCE')
CUPBOARD_TEST_CLIENT_ID = os.getenv('CUPBOARD_TEST_CLIENT_ID')
CUPBOARD_TEST_CLIENT_SECRET = os.getenv('CUPBOARD_TEST_CLIENT_SECRET')


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


def jwt_decode_token(token: str) -> dict:
    """
    Fetches the JWKS from Auth0 account to verify and decode the
    incoming Access Token.

    Args:
        token: The access token.

    Returns:
        Decoded access token in the form of dictionary.
    """
    header = jwt.get_unverified_header(token)
    result = {}
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
        public_key = None
        for jwk in jwks['keys']:
            if jwk['kid'] == header['kid']:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

        if public_key is None:
            raise Exception('Public key not found.')

        result = jwt.decode(
            token,
            public_key,
            audience=AUTH0_API_AUDIENCE,
            issuer=issuer,
            algorithms=['RS256']
        )
    return result


def jwt_get_token() -> dict:
    """
    Gets the test access token for Cupboard (Test Application)

    Returns:
        JSON object of the access_token, expiry_time, and token_type
    """
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)

    payload = (
        '{'
        f'"client_id":"{CUPBOARD_TEST_CLIENT_ID}",'
        f'"client_secret":"{CUPBOARD_TEST_CLIENT_SECRET}",'
        f'"audience":"{AUTH0_API_AUDIENCE}",'
        '"grant_type":"client_credentials"'
        '}'
    )

    headers = {'content-type': "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data)


def jwt_send_token(api_path: str, access_token: str) -> dict:
    """
    Sends the token to the API

    Args:
        api_path: api args i.e. /api/public
        access_token: Access token

    Returns:
        The returns JSON from the api call.
    """
    conn = http.client.HTTPConnection('localhost:{}'.format(PORT))

    headers = {'authorization': "Bearer {}".format(access_token)}
    conn.request("GET", api_path, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data)
