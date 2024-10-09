import os
from time import time
import jwt
import requests

from utils.env_helper import load_env_variables
# Reads the .env file and loads all the values
load_env_variables()

os.environ['TEST_RUN'] = 'true'

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')

# Test payload
TEST_KEY = os.getenv('TEST_KEY')
TEST_VALID_TOKEN_PAYLOAD = {
    "iss": 'https://{}/'.format(AUTH0_DOMAIN),
    "sub": "CupboardTest@clients",
    "aud": AUTH0_API_IDENTIFIER,
    "iat": time(),
    "exp": time() + 3600,
    "azp": "mK3brgMY0GIMox40xKWcUZBbv2Xs0YdG",
    "scope": "read:messages",
    "gty": "client-credentials",
    "permissions": [],
    "https://cupboard-teacup.com/email": "testing@cupboard.com",
}


def get_test_access_token() -> str:
    """
    Gets the access_token to run the tests using simple encryption for
    mock/test payloads.

    Returns:
        Access_token for the test payload or mock payload depending on DEV_LAYER
        environment variable.
    """
    return jwt.encode(TEST_VALID_TOKEN_PAYLOAD, TEST_KEY, algorithm='HS256')


# System Test for get all ingredients api
def test_get_all_ing_api():
    # Sends GET request to the  get all ingredients api

    response = requests.get(
        "http://localhost:" + str(os.getenv('DJANGO_PORT')) + "/api/get_all_ingredients",
        headers={'Authorization': "Bearer {}".format(get_test_access_token())}
    )
    print(response.json())
    data = response.json()

    # ensures received value from the request is in proper format in with expected information
    assert(any(entry['name'] == 'test_ingredient1' for entry in data['result']))
    assert(any(entry['name'] == 'test_ingredient2' for entry in data['result']))


# Runs all tests
def run_all_system_tests():
    test_get_all_ing_api()


run_all_system_tests()
