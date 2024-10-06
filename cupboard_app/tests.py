from django.test import TestCase
from .models import Ingredient
from .queries import get_all_ingredients
from .views import get_all_ingredients as views_get_all_ingredients
from django.http import HttpRequest
import json
import os
from time import time
import jwt
from rest_framework.reverse import reverse

from .views import (
    CRED_NOT_PROVIDED,
    TOKEN_DECODE_ERROR
)

# Mock payload
MOCK_DOMAIN = os.getenv('MOCK_DOMAIN')
MOCK_API_IDENTIFIER = os.getenv('MOCK_API_IDENTIFIER')
MOCK_KEY = os.getenv('MOCK_KEY')
MOCK_VALID_TOKEN_PAYLOAD = {
    "iss": 'https://{}/'.format(MOCK_DOMAIN),
    "sub": "user@clients",
    "aud": MOCK_API_IDENTIFIER,
    "iat": time(),
    "exp": time() + 3600,
    "azp": "mK3brgMY0GIMox40xKWcUZBbv2Xs0YdG",
    "scope": "read:messages",
    "gty": "client-credentials",
    "permissions": [],
}

# Test payload
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')
TEST_KEY = os.getenv('TEST_KEY')
TEST_VALID_TOKEN_PAYLOAD = {
    "iss": 'https://{}/'.format(AUTH0_DOMAIN),
    "sub": "user@clients",
    "aud": AUTH0_API_IDENTIFIER,
    "iat": time(),
    "exp": time() + 3600,
    "azp": "mK3brgMY0GIMox40xKWcUZBbv2Xs0YdG",
    "scope": "read:messages",
    "gty": "client-credentials",
    "permissions": [],
}

DEV_LAYER = os.getenv('DEV_LAYER', 'mock')

def get_access_token() -> str:
    """
    Gets the access_token to run the tests.

    Returns:
        access_token for the actual test cupboard application or
        creates an access_token for the mock.
    """
    token = None
    if DEV_LAYER == 'mock':
        token = jwt.encode(MOCK_VALID_TOKEN_PAYLOAD, str(MOCK_KEY), algorithm='HS256')
    else:
        token = jwt.encode(TEST_VALID_TOKEN_PAYLOAD, str(TEST_KEY), algorithm='HS256')

    return token

# Create your tests here.
class TestIngredients(TestCase):
    def setUp(self):
        Ingredient.objects.create(name="testing", type="TEST")
        Ingredient.objects.create(name="testing2", type="TEST2")
    def test_get_all_ingredients(self):
        ingredients_list = get_all_ingredients()
        for item in ingredients_list:
            #temp = json.loads(item)
            #print(temp["name"])
            print(item)

class TestAPIs(TestCase):
    def setUp(self):
        Ingredient.objects.create(name="testing", type="TEST")
        Ingredient.objects.create(name="testing2", type="TEST2")
    
    def test_get_all_ingredients(self):
        response = self.client.get(
            reverse('get_all_ingredients'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_access_token())
        )

        self.assertEqual(response.status_code, 200)
        print("OUTPUT: " + str(response.json()))