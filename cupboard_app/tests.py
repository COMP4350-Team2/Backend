import os
from time import time

import jwt
from django.test import TestCase
from rest_framework.reverse import reverse

from cupboard_app.models import Ingredient
from cupboard_app.queries import (
    CREATE_SUCCESS_MSG,
    get_all_ingredients
)

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


# DB Tests
class TestIngredients(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        Ingredient.objects.create(name="testing", type="TEST")
        Ingredient.objects.create(name="testing2", type="TEST2")

    def test_get_all_ingredients(self):
        """
        Testing get_all_ingredients retrieves all the ingredients
        from the database
        """
        ingredients_list = get_all_ingredients()
        for item in ingredients_list:
            print(item)


# API Tests
class PublicMessageApi(TestCase):
    def test_public_api_returns(self):
        """
        Testing the public api
        """
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
        """
        Testing the private api without a token
        """
        response = self.client.get(reverse('private'))
        self.assertEqual(response.status_code, 401)

    def test_private_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the private api with a invalid token
        """
        response = self.client.get(
            reverse('private'),
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        self.assertEqual(response.status_code, 401)

    def test_private_api_with_valid_token_returns_ok(self):
        """
        Testing the private api with a valid token
        """
        response = self.client.get(
            reverse('private'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_test_access_token())
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
        """
        Testing the private_scoped api without a token
        """
        response = self.client.get(reverse('private_scoped'))
        self.assertEqual(response.status_code, 401)

    def test_private_scoped_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the private_scoped api with a invalid token
        """
        response = self.client.get(
            reverse('private_scoped'),
            HTTP_AUTHORIZATION="Bearer invalid-token"
        )
        self.assertEqual(response.status_code, 401)

    def test_private_scoped_api_with_valid_token_returns_ok(self):
        """
        Testing the private_scoped api with a valid token
        """
        response = self.client.get(
            reverse('private_scoped'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_test_access_token())
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
        """
        Sets up a test database with test values
        """
        Ingredient.objects.create(name="testing", type="TEST")
        Ingredient.objects.create(name="testing2", type="TEST2")

    def test_get_all_ingredients(self):
        """
        Testing get_all_ingredients retrieves all the ingredients
        from the database
        """
        response = self.client.get(
            reverse('get_all_ingredients'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_test_access_token())
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'result': [
                    {'name': 'testing', 'type': 'TEST'},
                    {'name': 'testing2', 'type': 'TEST2'}
                ]
            }
        )


class CreateUser(TestCase):
    def test_create_user_without_token_returns_unauthorized(self):
        """
        Testing the create user api without a token
        """
        response = self.client.post(reverse('create_user'))
        self.assertEqual(response.status_code, 401)

    def test_create_user_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the create user api with a invalid token
        """
        response = self.client.post(
            reverse('create_user'),
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        self.assertEqual(response.status_code, 401)

    def test_create_user_api_with_valid_token_returns_ok(self):
        """
        Testing the create user api with a valid token
        """
        response = self.client.post(
            reverse('create_user'),
            HTTP_AUTHORIZATION="Bearer {}".format(get_test_access_token())
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': CREATE_SUCCESS_MSG
            }
        )
