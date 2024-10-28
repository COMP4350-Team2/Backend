import os
import json
from time import time
from unittest.mock import patch

from django.test import TestCase
from django.urls.exceptions import NoReverseMatch
from rest_framework.reverse import reverse
from rest_framework_simplejwt.backends import TokenBackend

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients
)
from cupboard_app.queries import (
    ADD_ACTION,
    REMOVE_ACTION,
    DOES_NOT_EXIST,
    INVALID_USER_LIST
)
from cupboard_app.views import (
    PublicMessageAPIView,
    PrivateMessageAPIView,
    PrivateScopedMessageAPIView,
    UserViewSet,
    UserListIngredientsViewSet,
    INVALID_TOKEN,
    NO_AUTH,
    PERMISSION_DENIED
)

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')

# Test payload
TEST_VALID_TOKEN_PAYLOAD = {
    'iss': 'https://{}/'.format(AUTH0_DOMAIN),
    'sub': 'CupboardTest@clients',
    'aud': AUTH0_API_IDENTIFIER,
    'iat': time(),
    'exp': time() + 3600,
    'azp': 'mK3brgMY0GIMox40xKWcUZBbv2Xs0YdG',
    'scope': 'read:messages',
    'gty': 'client-credentials',
    'permissions': ['read:messages'],
    'https://cupboard-teacup.com/email': 'testing@cupboard.com',
}
TEST_INVALID_TOKEN_PAYLOAD = {
    **TEST_VALID_TOKEN_PAYLOAD,
    'https://cupboard-teacup.com/email': None,
}


class PublicMessageApi(TestCase):
    def test_public_api_returns(self):
        """
        Testing the public API
        """
        response = self.client.get(reverse('public'))

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': PublicMessageAPIView.text
            }
        )


class PrivateMessageApi(TestCase):
    def test_private_api_without_token_returns_unauthorized(self):
        """
        Testing the private API without a token
        """
        response = self.client.get(reverse('private'))
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), NO_AUTH
        )

    def test_private_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the private API with a invalid token
        """
        response = self.client.get(
            reverse('private'),
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), INVALID_TOKEN
        )

    @patch.object(TokenBackend, 'decode')
    def test_private_api_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the private API with a valid token
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse('private'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': PrivateMessageAPIView.text
            }
        )


class PrivateScopedMessageApi(TestCase):
    def test_private_scoped_api_without_token_returns_unauthorized(self):
        """
        Testing the private_scoped API without a token
        """
        response = self.client.get(reverse('private_scoped'))
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), NO_AUTH
        )

    def test_private_scoped_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the private_scoped API with a invalid token
        """
        response = self.client.get(
            reverse('private_scoped'),
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), INVALID_TOKEN
        )

    @patch.object(TokenBackend, 'decode')
    def test_private_scoped_api_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the private_scoped API with a valid token
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse('private_scoped'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': PrivateScopedMessageAPIView.text
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_private_scoped_api_without_permissions(self, mock_decode):
        mock_decode.return_value = {
            **TEST_VALID_TOKEN_PAYLOAD,
            'permissions': [],
        }

        response = self.client.get(
            reverse('private_scoped'), HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), PERMISSION_DENIED)


class CreateUserApi(TestCase):
    def test_create_user_without_token_returns_unauthorized(self):
        """
        Testing the create user api without a token
        """
        response = self.client.post(reverse('user'))
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(response.json(), NO_AUTH)

    def test_create_user_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the create user api with a invalid token
        """
        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(response.json(), INVALID_TOKEN)

    @patch.object(TokenBackend, 'decode')
    def test_create_user_api_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the create user api with a valid token.
        We run the same request twice to check response when user already
        exists in the db.
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD
        username = TEST_VALID_TOKEN_PAYLOAD.get('sub')
        email = TEST_VALID_TOKEN_PAYLOAD.get('https://cupboard-teacup.com/email')

        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                'username': username,
                'email': email
            }
        )

        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                'username': username,
                'email': email
            }
        )

        user_result = User.objects.get(username=username)
        self.assertEqual(user_result.username, username)
        self.assertEqual(user_result.email, email)

    @patch.object(TokenBackend, 'decode')
    def test_create_user_api_without_email_token_returns_500(self, mock_decode):
        """
        Testing the create user api with a valid token that does not contain email.
        """
        mock_decode.return_value = TEST_INVALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {
                'message': UserViewSet.MISSING_USER_INFO
            }
        )


class CreateUserListIngredientsApi(TestCase):
    username = TEST_VALID_TOKEN_PAYLOAD.get('sub')
    email = TEST_VALID_TOKEN_PAYLOAD.get('https://cupboard-teacup.com/email')
    list_name = 'Grocery'
    list_name2 = 'Pantry'
    test_ing = 'Pork'
    test_unit = 'g'

    def setUp(self):
        """
        Sets up a test database with test values
        """
        User.objects.create(username=self.username, email=self.email)
        Ingredient.objects.create(name=self.test_ing, type='Meat')
        Measurement.objects.create(unit=self.test_unit)
        ListName.objects.create(list_name=self.list_name2)
        UserListIngredients.objects.create(
            user=User.objects.get(username=self.username),
            list_name=ListName.objects.get(list_name=self.list_name2),
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_create_list_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the create UserListIngredient API with a valid token and
        parameters.
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse('specific_user_list_ingredients', kwargs={'list_name': self.list_name}),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                'user': self.username,
                'list_name': self.list_name,
                'ingredients': []
            }
        )

        # Check how many lists we have
        result = UserListIngredients.objects.filter(
            user__username=self.username
        )
        self.assertEqual(len(result), 2)

        # Try creating same list again
        response = self.client.post(
            reverse('specific_user_list_ingredients', kwargs={'list_name': self.list_name}),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                'user': self.username,
                'list_name': self.list_name,
                'ingredients': []
            }
        )

        # Check list wasn't created again
        result = UserListIngredients.objects.filter(
            user__username=self.username
        )
        self.assertEqual(len(result), 2)

    @patch.object(TokenBackend, 'decode')
    def test_create_list_with_missing_parameter(self, mock_decode):
        """
        Testing the create UserListIngredients API with missing parameter
        """
        mock_decode.return_value = TEST_INVALID_TOKEN_PAYLOAD

        # Try with no parameter passed
        with self.assertRaises(NoReverseMatch):
            response = self.client.post(
                reverse('specific_user_list_ingredients'),
                HTTP_AUTHORIZATION='Bearer valid-token'
            )
        # Try with empty string parameter passed
        with self.assertRaises(NoReverseMatch):
            response = self.client.post(
                reverse('specific_user_list_ingredients', kwargs={'list_name': ''}),
                HTTP_AUTHORIZATION='Bearer valid-token'
            )

            self.assertEqual(response.status_code, 400)
            self.assertDictEqual(
                response.json(),
                {
                    'message': UserListIngredientsViewSet.MISSING_USER_LIST_PARAM_MSG
                }
            )


class GetAllIngredientsApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        Ingredient.objects.create(name='testing', type='TEST')
        Ingredient.objects.create(name='testing2', type='TEST2')

    @patch.object(TokenBackend, 'decode')
    def test_get_all_ingredients(self, mock_decode):
        """
        Testing get_all_ingredients retrieves all the ingredients
        from the database
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse('ingredients'),
            HTTP_AUTHORIZATION='Bearer valid-token'
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


class UpdateIngredientListApi(TestCase):
    user = None
    unit = None
    ing1 = None
    ing2 = None
    list_name = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user = User.objects.create(username='testuser', email='test@test.com')
        self.unit = Measurement.objects.create(unit='test_unit')
        self.ing1 = Ingredient.objects.create(name='test_ing', type='test_type')
        self.ing2 = Ingredient.objects.create(name='testing2', type='TEST2')
        self.list_name = ListName.objects.create(list_name='testlist')
        UserListIngredients.objects.create(
            user=self.user,
            list_name=self.list_name,
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list(self, mock_decode):
        """
        Testing adding an ingredient to an existing list
        """
        mock_decode.return_value = {
            **TEST_VALID_TOKEN_PAYLOAD,
            'sub': self.user.username
        }

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 5,
                    'unit': self.unit.unit,
                    'action': ADD_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        # ensures correct response given by view response
        self.assertEqual(
            response.json().get('ingredients'),
            [
                {
                    'ingredient_id': self.ing1.id,
                    'ingredient_name': self.ing1.name,
                    'amount': 5,
                    'unit_id': self.unit.id,
                    'unit': self.unit.unit
                }
            ]
        )

        # ensures the item was actually added to the list
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user.username,
            list_name__list_name=self.list_name.list_name
        ).first()
        self.assertEqual(
            modified_list.ingredients,
            [
                {
                    'ingredient_id': self.ing1.id,
                    'ingredient_name': self.ing1.name,
                    'amount': 5,
                    'unit_id': self.unit.id,
                    'unit': self.unit.unit
                }
            ]
        )

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_missing_data(self, mock_decode):
        """
        Testing adding an ingredient to an existing list when one
        of the required pieces of information are missing
        """
        mock_decode.return_value = {
            **TEST_VALID_TOKEN_PAYLOAD,
            'sub': self.user.username
        }

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 5
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 400)
        # ensures correct response given by view response
        self.assertDictEqual(
            response.json(),
            {
                'message': UserListIngredientsViewSet.MISSING_UPDATE_INGREDIENT_MSG
            }
        )

        # ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user.username,
            list_name__list_name=self.list_name.list_name
        ).first()
        self.assertEqual([], modified_list.ingredients)

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_incorect_data(self, mock_decode):
        """
        Testing adding an ingredient to an existing list with an
        incorrect value (i.e. user that does not actually exist)
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 5,
                    'unit': self.unit.unit,
                    'action': ADD_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 500)
        # ensures correct response given by view response
        self.assertEqual(response.json(), {'message': INVALID_USER_LIST})
        # ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user.username,
            list_name__list_name=self.list_name.list_name
        ).first()
        self.assertEqual([], modified_list.ingredients)

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_nonexisting_ing(self, mock_decode):
        """
        Testing adding an ingredient to an existing list with an ingredient
        that does not actually exist
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': 'test_ing_fake',
                    'amount': 5,
                    'unit': self.unit.unit,
                    'action': ADD_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 500)
        # ensures correct response given by view response
        self.assertDictEqual(
            response.json(),
            {
                'message': f'Ingredient {DOES_NOT_EXIST}'
            }
        )
        # ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user.username,
            list_name__list_name=self.list_name.list_name
        ).first()
        self.assertEqual([], modified_list.ingredients)

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_list(self, mock_decode):
        """
        Testing removing an ingredient from an existing list
        """
        mock_decode.return_value = {
            **TEST_VALID_TOKEN_PAYLOAD,
            'sub': self.user.username
        }

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 100,
                    'unit': self.unit.unit,
                    'action': ADD_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 50,
                    'unit': self.unit.unit,
                    'action': REMOVE_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        # ensures remove is working when remove amount is less than amount in the list
        self.assertEqual(
            response.json().get('ingredients'),
            [
                {
                    'ingredient_id': self.ing1.id,
                    'ingredient_name': self.ing1.name,
                    'amount': 50,
                    'unit_id': self.unit.id,
                    'unit': self.unit.unit
                }
            ]
        )

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 50,
                    'unit': self.unit.unit,
                    'action': REMOVE_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        # ensures ingredient was removed when the exact amount in the list is being removed
        self.assertEqual(response.json().get('ingredients'), [])

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 100,
                    'unit': self.unit.unit,
                    'action': ADD_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        # ensures remove is working as expected
        self.assertEqual(
            response.json().get('ingredients'),
            [
                {
                    'ingredient_id': self.ing1.id,
                    'ingredient_name': self.ing1.name,
                    'amount': 100,
                    'unit_id': self.unit.id,
                    'unit': self.unit.unit
                }
            ]
        )

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 120,
                    'unit': self.unit.unit,
                    'action': REMOVE_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        # ensures ingredient was removed when more amount in the list is being removed
        self.assertEqual(response.json().get('ingredients'), [])

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_list_nonexisting_ing(self, mock_decode):
        """
        Testing removing an ingredient from empty list
        """
        mock_decode.return_value = {
            **TEST_VALID_TOKEN_PAYLOAD,
            'sub': self.user.username
        }

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 120,
                    'unit': self.unit.unit,
                    'action': REMOVE_ACTION
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        # ensures correct response given by view response
        self.assertEqual(response.json().get('ingredients'), [])
