import os
from time import time

import jwt
from django.test import TestCase
from rest_framework.reverse import reverse

from .models import Ingredient
from .queries import get_all_ingredients
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


# API tests
class PublicMessageApi(TestCase):
    def test_public_api_returns(self):
        response = self.client.get(reverse('public'))

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': (
                    'Hello from a public endpoint! '
                    'You don\'t need to be authenticated to see this.'
                )
            }
        )


class PrivateMessageApi(TestCase):
    def test_private_api_without_token_returns_unauthorized(self):
        response = self.client.get(reverse('private'))

        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(),
            CRED_NOT_PROVIDED
        )

    def test_private_api_with_invalid_token_returns_unauthorized(self):
        response = self.client.get(
            reverse('private'),
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )

        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(),
            TOKEN_DECODE_ERROR
        )

    def test_private_api_with_valid_token_returns_ok(self):
        response = self.client.get(
            reverse('private'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_access_token())
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': (
                    'Hello from a private endpoint! '
                    'You need to be authenticated to see this.'
                )
            }
        )


class PrivateScopedMessageApi(TestCase):
    def test_private_scoped_api_without_token_returns_unauthorized(self):
        response = self.client.get(reverse('private-scoped'))

        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(),
            CRED_NOT_PROVIDED
        )

    def test_private_scoped_api_with_invalid_token_returns_unauthorized(self):
        response = self.client.get(
            reverse('private-scoped'),
            HTTP_AUTHORIZATION="Bearer invalid-token"
        )

        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(),
            TOKEN_DECODE_ERROR
        )

    def test_private_scoped_api_with_valid_token_returns_ok(self):

        response = self.client.get(
            reverse('private-scoped'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_access_token())
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': (
                    'Hello from a private endpoint! '
                    'You need to be authenticated and have a scope of '
                    'read:messages to see this.'
                )
            }
        )

class GetAllIngredientsApi(TestCase):
    def setUp(self):
        Ingredient.objects.create(name="testing", type="TEST")
        Ingredient.objects.create(name="testing2", type="TEST2")

    def test_get_all_ingredients(self):
        response = self.client.get(
            reverse('get_all_ingredients'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_access_token())
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'result':[
                    {'name':'testing', 'type':'TEST'},
                    {'name':'testing2', 'type':'TEST2'}
                ]
            }
        )
