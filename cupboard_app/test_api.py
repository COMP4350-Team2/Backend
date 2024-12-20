import os
import json
from time import time
from unittest.mock import patch
from urllib.parse import urlencode

from django.test import TestCase
from django.urls.exceptions import NoReverseMatch
from rest_framework.reverse import reverse
from rest_framework_simplejwt.backends import TokenBackend

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients,
    CustomIngredient,
    Recipe
)
from cupboard_app.queries import (
    CANNOT_CREATE_INGREDIENT,
    DOES_NOT_EXIST,
    GROCERY_LIST_NAME,
    PANTRY_LIST_NAME,
    INVALID_RECIPE,
    INVALID_USER_LIST,
    MAX_LISTS,
    MAX_LISTS_PER_USER
)
from cupboard_app.views import (
    UserViewSet,
    UserListIngredientsViewSet,
    UpdateUserListIngredientsViewSet
)

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')
API_VERSION = 'v3'
CUPBOARD_EMAIL_CLAIM = 'https://cupboard-teacup.com/email'

# Test payload
USER_VALID_TOKEN_PAYLOAD = {
    'iss': 'https://{}/'.format(AUTH0_DOMAIN),
    'sub': 'CupboardTest@clients',
    'aud': AUTH0_API_IDENTIFIER,
    'iat': time(),
    'exp': time() + 3600,
    'azp': 'mK3brgMY0GIMox40xKWcUZBbv2Xs0YdG',
    'scope': 'read:messages',
    'gty': 'client-credentials',
    'permissions': ['read:messages'],
    CUPBOARD_EMAIL_CLAIM: 'testing@cupboard.com',
}
TEST_INVALID_TOKEN_PAYLOAD = {
    **USER_VALID_TOKEN_PAYLOAD,
    CUPBOARD_EMAIL_CLAIM: None,
}


class GetUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    unit1 = None
    list_name1 = None
    list_name2 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name2,
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_get_all_lists_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the get all UserListIngredient API with a valid token and
        parameters.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(f'{API_VERSION}:user_list_ingredients'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Check how many lists we have
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(
            response.json(),
            [
                {
                    'user': self.user1.username,
                    'list_name': self.list_name1.list_name,
                    'ingredients': []
                },
                {
                    'user': self.user1.username,
                    'list_name': self.list_name2.list_name,
                    'ingredients': []
                }
            ]
        )


class CreateUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    unit1 = None
    list_name1 = None
    list_name2 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_create_list(self, mock_decode):
        """
        Testing the create UserListIngredient API.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': self.list_name2.list_name}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name2.list_name,
                'ingredients': []
            }
        )

        # Check how many lists we have
        result = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(result), 2)

        # Try creating same list again
        response = self.client.post(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': self.list_name2.list_name}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name2.list_name,
                'ingredients': []
            }
        )

        # Check list wasn't created again
        result = UserListIngredients.objects.filter(user__username=self.user1.username)
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
                reverse(f'{API_VERSION}:specific_user_list_ingredients'),
                HTTP_AUTHORIZATION='Bearer valid-token'
            )

        # Try with empty string parameter passed
        with self.assertRaises(NoReverseMatch):
            response = self.client.post(
                reverse(f'{API_VERSION}:specific_user_list_ingredients', kwargs={'list_name': ''}),
                HTTP_AUTHORIZATION='Bearer valid-token'
            )

            self.assertEqual(response.status_code, 400)
            self.assertDictEqual(
                response.json(),
                {'message': UserListIngredientsViewSet.MISSING_USER_LIST_PARAM_MSG}
            )

    @patch.object(TokenBackend, 'decode')
    def test_create_max_lists(self, mock_decode):
        """
        Testing the maximum create UserListIngredient API.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        result = UserListIngredients.objects.filter(user__username=self.user1.username)

        for i in range(MAX_LISTS - len(result)):
            response = self.client.post(
                reverse(
                    f'{API_VERSION}:specific_user_list_ingredients',
                    kwargs={'list_name': f'test_listname{i}'}
                ),
                HTTP_AUTHORIZATION='Bearer valid-token'
            )

            self.assertEqual(response.status_code, 201)

        # Check how many lists we have
        result = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(result), MAX_LISTS)

        response = self.client.post(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': f'test_listname{MAX_LISTS}'}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message': MAX_LISTS_PER_USER})

        # Check how many lists we have
        result = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(result), MAX_LISTS)


class GetSpecificUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    unit1 = None
    list_name1 = None
    list_name2 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name2,
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_get_specific_list(self, mock_decode):
        """
        Testing the get specific UserListIngredient API.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': self.list_name1.list_name}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Check how many lists we have
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name1.list_name,
                'ingredients': []
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_get_invalid_specific_list(self, mock_decode):
        """
        Testing the get specific UserListIngredient API when the list doesn't exist
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': 'nonexistent'}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Check how many lists we have
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message': INVALID_USER_LIST})


class ChangeUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    unit1 = None
    list_name1 = None
    list_name2 = None
    list_ing1 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        self.list_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 500,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[self.list_ing1]
        )

    @patch.object(TokenBackend, 'decode')
    def test_change_user_list_ingredients_name(self, mock_decode):
        """
        Testing the change UserListIngredient name API with a valid parameters.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse(f'{API_VERSION}:user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'new_list_name': self.list_name2.list_name
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Make sure user has the correct response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name2.list_name,
                'ingredients': [self.list_ing1]
            }
        )

        # Make sure user only has one list and it is correct
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 1)
        self.assertEqual(user_lists[0].user, self.user1)
        self.assertEqual(user_lists[0].list_name, self.list_name2)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])

    @patch.object(TokenBackend, 'decode')
    def test_change_invalid_user_list_ingredients_name(self, mock_decode):
        """
        Testing the change UserListIngredient name API when the list doesn't exist.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse(f'{API_VERSION}:user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'new_list_name': self.list_name1.list_name
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message': INVALID_USER_LIST})

        # Make sure user has the correct list and it is correct
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 1)
        self.assertEqual(user_lists[0].user, self.user1)
        self.assertEqual(user_lists[0].list_name, self.list_name1)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])


class DeleteUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    unit1 = None
    list_name1 = None
    list_name2 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name2,
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_delete_user_list_ingredients(self, mock_decode):
        """
        Testing the delete UserListIngredient API with a valid parameters.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': self.list_name1.list_name}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Check how many lists we have
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json(),
            [
                {
                    'user': self.user1.username,
                    'list_name': self.list_name2.list_name,
                    'ingredients': []
                }
            ]
        )

    @patch.object(TokenBackend, 'decode')
    def test_delete_user_list_ingredients_when_empty(self, mock_decode):
        """
        Testing the delete UserListIngredient API when the user has no lists
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': self.list_name1.list_name}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': self.list_name2.list_name}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Check how many lists we have
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        # Try delete again when there is nothing
        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_user_list_ingredients',
                kwargs={'list_name': self.list_name2.list_name}
            ),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class AddIngredientUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    ing2 = None
    unit1 = None
    list_name1 = None
    list_name2 = None
    list_ing1 = None
    list_cust_ing1 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type2')
        self.cust_ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        self.list_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 5,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        self.list_cust_ing1 = {
            'ingredient_name': self.cust_ing1.name,
            'ingredient_type': self.cust_ing1.type,
            'amount': 5,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list(self, mock_decode):
        """
        Testing adding an ingredient to an existing list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name1.list_name,
                    'ingredient': self.ing1.name,
                    'amount': self.list_ing1.get('amount'),
                    'unit': self.unit1.unit,
                    'is_custom_ingredient': False
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('ingredients'), [self.list_ing1])

        # Ensures the item was actually added to the list
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [self.list_ing1])

        # Test adding custom ingredient to the list
        response = self.client.post(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name1.list_name,
                    'ingredient': self.list_cust_ing1.get('ingredient_name'),
                    'amount': self.list_cust_ing1.get('amount'),
                    'unit': self.list_cust_ing1.get('unit'),
                    'is_custom_ingredient': self.list_cust_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('ingredients'), [self.list_ing1, self.list_cust_ing1])

        # Ensures the item was actually added to the list
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [self.list_ing1, self.list_cust_ing1])

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_missing_data(self, mock_decode):
        """
        Testing adding an ingredient to an existing list when one
        of the required pieces of information are missing
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name1.list_name,
                    'ingredient': self.ing1.name,
                    'amount': 5
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {'message': UpdateUserListIngredientsViewSet.MISSING_ADD_INGREDIENT_MSG}
        )

        # Ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_incorrect_list(self, mock_decode):
        """
        Testing adding an ingredient to a list that doesn't exist
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'list_name': 'Does not exist',
                    'ingredient': self.ing1.name,
                    'amount': 5,
                    'unit': self.unit1.unit,
                    'is_custom_ingredient': False
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message': INVALID_USER_LIST})

        # Ensures the list items have not been changed
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 1)
        self.assertEqual(user_lists[0].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_nonexisting_ingredient(self, mock_decode):
        """
        Testing adding an ingredient to an existing list with an ingredient
        that does not actually exist
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name1.list_name,
                    'ingredient': 'test_ingredient_fake',
                    'amount': 5,
                    'unit': self.unit1.unit,
                    'is_custom_ingredient': False
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(
            response.json(),
            {'message': f'Ingredient {DOES_NOT_EXIST}'}
        )

        # Ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [])


class SetIngredientUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    ing2 = None
    unit1 = None
    unit2 = None
    list_name1 = None
    list_name2 = None
    list_ing1 = None
    list_ing2 = None
    list_cust_ing1 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type2')
        self.cust_ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.unit2 = Measurement.objects.create(unit='test_unit2')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        self.list_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 50,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        self.list_ing2 = {
            'ingredient_name': self.ing2.name,
            'ingredient_type': self.ing2.type,
            'amount': 50,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        self.list_cust_ing1 = {
            'ingredient_name': self.cust_ing1.name,
            'ingredient_type': self.cust_ing1.type,
            'amount': 50,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[self.list_ing1]
        )
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name2,
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_set_ingredient_in_list(self, mock_decode):
        """
        Testing setting an ingredient in an existing list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        # Changing amount of an ingredient
        updated_ing1 = {
            **self.list_ing1,
            'amount': self.list_ing1.get('amount') + 10
        }
        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': self.list_ing1.get('ingredient_name'),
                    'old_amount': self.list_ing1.get('amount'),
                    'old_unit': self.list_ing1.get('unit'),
                    'old_is_custom_ingredient': self.list_ing1.get('is_custom_ingredient'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': updated_ing1.get('ingredient_name'),
                    'new_amount': updated_ing1.get('amount'),
                    'new_unit': updated_ing1.get('unit'),
                    'new_is_custom_ingredient': updated_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get('ingredients'), [updated_ing1])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [updated_ing1])

        # Changing unit of an ingredient
        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'old_is_custom_ingredient': updated_ing1.get('is_custom_ingredient'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': updated_ing1.get('ingredient_name'),
                    'new_amount': updated_ing1.get('amount'),
                    'new_unit': self.unit2.unit,
                    'new_is_custom_ingredient': updated_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        updated_ing1 = {
            **updated_ing1,
            'unit': self.unit2.unit
        }

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get('ingredients'), [updated_ing1])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [updated_ing1])

        # Changing unit and amount of an ingredient
        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'old_is_custom_ingredient': updated_ing1.get('is_custom_ingredient'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': self.list_ing1.get('ingredient_name'),
                    'new_amount': self.list_ing1.get('amount'),
                    'new_unit': self.list_ing1.get('unit'),
                    'new_is_custom_ingredient': self.list_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get('ingredients'), [self.list_ing1])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [self.list_ing1])

        # Test changing two same ingredients in the list but with different units
        # to the same unit
        list_name3 = ListName.objects.create(list_name='Fridge')
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=list_name3,
            ingredients=[
                self.list_ing1,
                {**self.list_ing1, 'unit': self.unit2.unit}
            ]
        )

        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': list_name3.list_name,
                    'old_ingredient': self.list_ing1.get('ingredient_name'),
                    'old_amount': self.list_ing1.get('amount'),
                    'old_unit': self.unit2.unit,
                    'old_is_custom_ingredient': self.list_ing1.get('is_custom_ingredient'),
                    'new_list_name': list_name3.list_name,
                    'new_ingredient': self.list_ing1.get('ingredient_name'),
                    'new_amount': self.list_ing1.get('amount'),
                    'new_unit': self.list_ing1.get('unit'),
                    'new_is_custom_ingredient': self.list_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        updated_ing1 = {
            **self.list_ing1,
            'amount': self.list_ing1.get('amount') * 2
        }

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[2].get('ingredients'), [updated_ing1])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=list_name3
        ).first()
        self.assertEqual(modified_list.ingredients, [updated_ing1])

        # Set custom ingredient
        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': list_name3.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'old_is_custom_ingredient': updated_ing1.get('is_custom_ingredient'),
                    'new_list_name': list_name3.list_name,
                    'new_ingredient': self.list_cust_ing1.get('ingredient_name'),
                    'new_amount': self.list_cust_ing1.get('amount'),
                    'new_unit': self.list_cust_ing1.get('unit'),
                    'new_is_custom_ingredient': self.list_cust_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[2].get('ingredients'), [self.list_cust_ing1])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=list_name3
        ).first()
        self.assertEqual(modified_list.ingredients, [self.list_cust_ing1])

    @patch.object(TokenBackend, 'decode')
    def test_set_ingredient_not_in_list(self, mock_decode):
        """
        Testing setting an ingredient not in the list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': self.list_ing2.get('ingredient_name'),
                    'old_amount': 0,
                    'old_unit': self.list_ing2.get('unit'),
                    'old_is_custom_ingredient': self.list_ing2.get('is_custom_ingredient'),
                    'new_list_name': self.list_name2.list_name,
                    'new_ingredient': self.list_ing2.get('ingredient_name'),
                    'new_amount': self.list_ing2.get('amount'),
                    'new_unit': self.list_ing2.get('unit'),
                    'new_is_custom_ingredient': self.list_ing2.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1].get('ingredients'), [self.list_ing2])

        # ensures the item was actually added to the list
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name2.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [self.list_ing2])

    @patch.object(TokenBackend, 'decode')
    def test_set_ingredient_in_list_missing_data(self, mock_decode):
        """
        Testing setting an ingredient to an existing list when one
        of the required pieces of information are missing
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': self.ing2.name,
                    'old_unit': self.unit1.unit,
                    'new_list_name': self.list_name2.list_name,
                    'new_ingredient': self.ing2.name,
                    'new_amount': self.list_ing2.get('amount'),
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {'message': UpdateUserListIngredientsViewSet.MISSING_SET_INGREDIENT_MSG}
        )

        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_set_ingredient_in_list_incorrect_list(self, mock_decode):
        """
        Testing setting an ingredient in a list that doesn't exist
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': 'Does not exist',
                    'old_ingredient': self.list_ing2.get('ingredient_name'),
                    'old_amount': 0,
                    'old_unit': self.list_ing2.get('unit'),
                    'old_is_custom_ingredient': self.list_ing2.get('is_custom_ingredient'),
                    'new_list_name': 'Does not exist',
                    'new_ingredient': self.list_ing2.get('ingredient_name'),
                    'new_amount': self.list_ing2.get('amount'),
                    'new_unit': self.list_ing2.get('unit'),
                    'new_is_custom_ingredient': self.list_ing2.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message': INVALID_USER_LIST})

        # Ensures the list items have not been changed
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_set_ingredient_in_list_nonexisting_ing(self, mock_decode):
        """
        Testing setting an ingredient that does not exist in an existing list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': self.list_ing2.get('ingredient_name'),
                    'old_amount': 0,
                    'old_unit': self.list_ing2.get('unit'),
                    'old_is_custom_ingredient': self.list_ing2.get('is_custom_ingredient'),
                    'new_list_name': self.list_name2.list_name,
                    'new_ingredient': 'Does not exist',
                    'new_amount': self.list_ing2.get('amount'),
                    'new_unit': self.list_ing2.get('unit'),
                    'new_is_custom_ingredient': self.list_ing2.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(
            response.json(),
            {'message': f'Ingredient {DOES_NOT_EXIST}'}
        )

        # Ensures the list items have not been changed
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_move_ingredient_in_list_to_another_list(self, mock_decode):
        """
        Testing moving an ingredient from one list to another list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        # Full amount of the ingredient moved from one list to another list
        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': self.list_ing1.get('ingredient_name'),
                    'old_amount': self.list_ing1.get('amount'),
                    'old_unit': self.list_ing1.get('unit'),
                    'old_is_custom_ingredient': self.list_ing1.get('is_custom_ingredient'),
                    'new_list_name': self.list_name2.list_name,
                    'new_ingredient': self.list_ing1.get('ingredient_name'),
                    'new_amount': self.list_ing1.get('amount'),
                    'new_unit': self.list_ing1.get('unit'),
                    'new_is_custom_ingredient': self.list_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get('ingredients'), [])
        self.assertEqual(result[1].get('ingredients'), [self.list_ing1])

        # Ensures the item was actually added to the list and removed from the other
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name2.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [self.list_ing1])

        # Partial amount of the ingredient moved from one list to another list
        updated_ing1 = {
            **self.list_ing1,
            'amount': self.list_ing1.get('amount') / 2
        }

        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'old_is_custom_ingredient': updated_ing1.get('is_custom_ingredient'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': updated_ing1.get('ingredient_name'),
                    'new_amount': updated_ing1.get('amount'),
                    'new_unit': updated_ing1.get('unit'),
                    'new_is_custom_ingredient': updated_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get('ingredients'), [updated_ing1])
        self.assertEqual(result[1].get('ingredients'), [updated_ing1])

        # Ensures the item was actually added to the list and removed from the other
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [updated_ing1])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name2.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [updated_ing1])

        # Test moving custom ingredient
        response = self.client.patch(
            reverse(f'{API_VERSION}:edit_user_list_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'old_is_custom_ingredient': updated_ing1.get('is_custom_ingredient'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': self.list_cust_ing1.get('ingredient_name'),
                    'new_amount': self.list_cust_ing1.get('amount'),
                    'new_unit': self.list_cust_ing1.get('unit'),
                    'new_is_custom_ingredient': self.list_cust_ing1.get('is_custom_ingredient')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get('ingredients'), [updated_ing1, self.list_cust_ing1])
        self.assertEqual(result[1].get('ingredients'), [])

        # Ensures the item was actually added to the list and removed from the other
        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name1.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [updated_ing1, self.list_cust_ing1])

        modified_list = UserListIngredients.objects.filter(
            user__username=self.user1.username,
            list_name__list_name=self.list_name2.list_name
        ).first()
        self.assertEqual(modified_list.ingredients, [])


class DeleteIngredientUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    ing2 = None
    unit1 = None
    list_name1 = None
    list_name2 = None
    list_name3 = None
    list_ing1 = None
    list_cust_ing1 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type2')
        self.cust_ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        self.list_name3 = ListName.objects.create(list_name='custom_list')
        self.list_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 5,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        self.list_cust_ing1 = {
            'ingredient_name': self.cust_ing1.name,
            'ingredient_type': self.cust_ing1.type,
            'amount': 5,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[self.list_ing1]
        )
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name2,
            ingredients=[]
        )
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name3,
            ingredients=[self.list_cust_ing1]
        )

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_list(self, mock_decode):
        """
        Testing removing an ingredient from an existing list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {
            'list_name': self.list_name1.list_name,
            'ingredient': self.ing1.name,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(f'{API_VERSION}:edit_user_list_ingredients'),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures remove is working normally
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name1.list_name,
                'ingredients': []
            }
        )

        # Check the database values as well
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 3)
        self.assertEqual(user_lists[0].ingredients, [])
        self.assertEqual(user_lists[1].ingredients, [])
        self.assertEqual(user_lists[2].ingredients, [self.list_cust_ing1])

        # Test deleting a custom ingredient
        query_params = {
            'list_name': self.list_name3.list_name,
            'ingredient': self.list_cust_ing1.get('ingredient_name'),
            'unit': self.list_cust_ing1.get('unit'),
            'is_custom_ingredient': self.list_cust_ing1.get('is_custom_ingredient')
        }
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(f'{API_VERSION}:edit_user_list_ingredients'),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures remove is working normally
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name3.list_name,
                'ingredients': []
            }
        )

        # Check the database values as well
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 3)
        self.assertEqual(user_lists[0].ingredients, [])
        self.assertEqual(user_lists[1].ingredients, [])
        self.assertEqual(user_lists[2].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_empty_list(self, mock_decode):
        """
        Testing removing an ingredient from an existing list when list is empty
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {
            'list_name': self.list_name2.list_name,
            'ingredient': self.ing1.name,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(f'{API_VERSION}:edit_user_list_ingredients'),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures remove is working normally
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name2.list_name,
                'ingredients': []
            }
        )

        # Check the database values as well
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 3)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])
        self.assertEqual(user_lists[2].ingredients, [self.list_cust_ing1])

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_list_incorrect_list(self, mock_decode):
        """
        Testing removing an ingredient from a list that doesn't exist
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {
            'list_name': 'Does not exist',
            'ingredient': self.ing1.name,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(f'{API_VERSION}:edit_user_list_ingredients'),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message': INVALID_USER_LIST})

        # Ensures the list items have not been changed
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 3)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])
        self.assertEqual(user_lists[2].ingredients, [self.list_cust_ing1])

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_list_nonexisting_ingredient(self, mock_decode):
        """
        Testing removing a nonexisting ingredient from list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {
            'list_name': self.list_name2.list_name,
            'ingredient': 'nonexisting_ingredient',
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(f'{API_VERSION}:edit_user_list_ingredients'),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'list_name': self.list_name2.list_name,
                'ingredients': []
            }
        )

        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 3)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])
        self.assertEqual(user_lists[2].ingredients, [self.list_cust_ing1])


class GetAllIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    ing2 = None
    cust_ing1 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type2')
        self.cust_ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )

    @patch.object(TokenBackend, 'decode')
    def test_get_all_ingredients(self, mock_decode):
        """
        Testing get_all_ingredients retrieves all the ingredients
        from the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(f'{API_VERSION}:ingredients'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'common_ingredients': [
                    {'name': self.ing1.name, 'type': self.ing1.type},
                    {'name': self.ing2.name, 'type': self.ing2.type}
                ],
                'custom_ingredients': [
                    {
                        'user': self.user1.username,
                        'name': self.cust_ing1.name,
                        'type': self.cust_ing1.type
                    }
                ]
            }
        )


class GetAllMeasurementsApi(TestCase):
    unit1 = None
    unit2 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.unit2 = Measurement.objects.create(unit='test_unit2')

    @patch.object(TokenBackend, 'decode')
    def test_get_all_measurements(self, mock_decode):
        """
        Testing get_all_measurements retrieves all the ingredients
        from the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(f'{API_VERSION}:measurements'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {'unit': self.unit1.unit},
                {'unit': self.unit2.unit}
            ]
        )


class CreateUserApi(TestCase):
    @patch.object(TokenBackend, 'decode')
    def test_create_user_api(self, mock_decode):
        """
        Testing the create user api.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD
        username = USER_VALID_TOKEN_PAYLOAD.get('sub')
        email = USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)

        response = self.client.post(
            reverse(f'{API_VERSION}:user'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {'username': username, 'email': email}
        )

        # Try calling creating the same user again doesn't create a new user
        response = self.client.post(
            reverse(f'{API_VERSION}:user'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {'username': username, 'email': email}
        )
        self.assertEqual(len(User.objects.all()), 1)

        user = User.objects.get(username=username)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)

        user_lists = UserListIngredients.objects.filter(user__username=username)
        grocery = ListName.objects.get(list_name=GROCERY_LIST_NAME)
        pantry = ListName.objects.get(list_name=PANTRY_LIST_NAME)

        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].user.username, username)
        self.assertEqual(user_lists[0].user.email, email)
        self.assertEqual(user_lists[0].list_name, grocery)
        self.assertEqual(user_lists[0].ingredients, [])

        self.assertEqual(user_lists[1].user.username, username)
        self.assertEqual(user_lists[1].user.email, email)
        self.assertEqual(user_lists[1].list_name, pantry)
        self.assertEqual(user_lists[1].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_create_user_api_without_email_in_token(self, mock_decode):
        """
        Testing the create user api with a valid token that does not contain email.
        """
        mock_decode.return_value = {
            **USER_VALID_TOKEN_PAYLOAD,
            CUPBOARD_EMAIL_CLAIM: None,
        }

        response = self.client.post(
            reverse(f'{API_VERSION}:user'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {'message': UserViewSet.MISSING_USER_INFO}
        )


class CreateCustomIngredientsApi(TestCase):
    unit1 = None
    unit2 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )

        self.cust_ing = {
            'user': self.user1.username,
            'name': 'Beef',
            'type': 'Meat'
        }

    @patch.object(TokenBackend, 'decode')
    def test_create_custom_ingredient(self, mock_decode):
        """
        Testing create_custom_ingredient creates a custom ingredient
        in the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD
        response = self.client.post(
            reverse(f'{API_VERSION}:custom_ingredient'),
            json.dumps(
                {
                    'ingredient': self.cust_ing['name'],
                    'type': self.cust_ing['type']
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(), self.cust_ing)

        # Test creation when the ingredient is one of the common ingredients
        common_ing = Ingredient.objects.create(name='common_ingredient', type='test_type1')
        response = self.client.post(
            reverse(f'{API_VERSION}:custom_ingredient'),
            json.dumps(
                {
                    'ingredient': common_ing.name,
                    'type': common_ing.type
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message': CANNOT_CREATE_INGREDIENT})

    @patch.object(TokenBackend, 'decode')
    def test_create_custom_ingredient_nonexistant_user(self, mock_decode):
        """
        Testing create_custom_ingredient works properly when
        a username doesn't exist in a custom ingredient
        """
        mock_decode.return_value = {**USER_VALID_TOKEN_PAYLOAD, 'sub': 'fake_user'}

        response = self.client.post(
            reverse(f'{API_VERSION}:custom_ingredient'),
            json.dumps(
                {
                    'ingredient': self.cust_ing['name'],
                    'type': self.cust_ing['type']
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 404)


class DeleteCustomIngredientsApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.cust_ing = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name='test_listname1')
        self.list_cust_ing1 = {
            'ingredient_name': self.cust_ing.name,
            'ingredient_type': self.cust_ing.type,
            'amount': 500,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        self.list1 = UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[self.list_cust_ing1]
        )

    @patch.object(TokenBackend, 'decode')
    def test_delete_custom_ingredient(self, mock_decode):
        """
        Testing delete_custom_ingredient deletes a custom ingredient
        in the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_custom_ingredient',
                kwargs={'ingredient': self.cust_ing.name}
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(list.ingredients), 0)

    @patch.object(TokenBackend, 'decode')
    def test_delete_nonexistant_custom_ingredient(self, mock_decode):
        """
        Testing delete_custom_ingredient works properly when a custom
        ingredient to be deleted isnt found in the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_custom_ingredient',
                kwargs={'ingredient': 'does_not_exist'}
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    'user': self.cust_ing.user.username,
                    'name': self.cust_ing.name,
                    'type': self.cust_ing.type
                }
            ]
        )


class CreateRecipeApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )

        self.recipe = {
            'user': self.user1.username,
            'recipe_name': 'My_Recipe',
            'steps': [],
            'ingredients': []
        }

    @patch.object(TokenBackend, 'decode')
    def test_create_recipe(self, mock_decode):
        """
        Testing create_recipe makes a recipe for the user
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(
                f'{API_VERSION}:specific_recipe',
                kwargs={'recipe_name': self.recipe['recipe_name']}
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.recipe)

    @patch.object(TokenBackend, 'decode')
    def test_create_recipe_nonexistant_user(self, mock_decode):
        """
        Testing create_recipe works properly when
        a username doesn't exist in a recipe
        """
        mock_decode.return_value = {**USER_VALID_TOKEN_PAYLOAD, 'sub': 'fake_user'}

        response = self.client.post(
            reverse(
                f'{API_VERSION}:specific_recipe',
                kwargs={'recipe_name': self.recipe['recipe_name']}
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 404)


class DeleteRecipeApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )

        self.recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name='My_Recipe2',
            steps=[],
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_delete_recipe(self, mock_decode):
        """
        Testing delete_recipe deletes a user's recipe.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_recipe',
                kwargs={'recipe_name': self.recipe.recipe_name}
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch.object(TokenBackend, 'decode')
    def test_delete_nonexistant_recipe(self, mock_decode):
        """
        Testing delete_recipe works properly when given
        a non-existant recipe
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:specific_recipe',
                kwargs={'recipe_name': 'doesnt_exist'}
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    'user': self.user1.username,
                    'recipe_name': 'My_Recipe2',
                    'steps': [],
                    'ingredients': []
                }
            ]
        )


class GetRecipeApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )

        self.recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name='My_Recipe2',
            steps=[],
            ingredients=[]
        )

        self.recipe2 = Recipe.objects.create(
            user=self.user1,
            recipe_name='My_Recipe3',
            steps=[],
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_get_recipe(self, mock_decode):
        """
        Testing get_recipe retrieves a specific recipe
        for the user
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(
                f'{API_VERSION}:specific_recipe',
                kwargs={'recipe_name': self.recipe2.recipe_name},
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': 'My_Recipe3',
                'steps': [],
                'ingredients': []
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_get_nonexistant_recipe(self, mock_decode):
        """
        Testing get_recipes works properly when a user's
        recipe isnt found in the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(
                f'{API_VERSION}:specific_recipe',
                kwargs={'recipe_name': 'doesnt_exist'},
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                'message': INVALID_RECIPE
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_get_all_recipes(self, mock_decode):
        """
        Testing get_all_recipes retrieves all the recipes
        for the user
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse(f'{API_VERSION}:recipe'),
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    'user': self.user1.username,
                    'recipe_name': 'My_Recipe2',
                    'steps': [],
                    'ingredients': []
                },
                {
                    'user': self.user1.username,
                    'recipe_name': 'My_Recipe3',
                    'steps': [],
                    'ingredients': []
                }
            ]
        )


class RecipeStepApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )

        self.step1 = "My first step!"
        self.step2 = "My second step!"

        self.recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name='My_Recipe2',
            steps=[],
            ingredients=[]
        )

        self.recipe2 = Recipe.objects.create(
            user=self.user1,
            recipe_name='My_Recipe3',
            steps=[self.step1],
            ingredients=[]
        )

    @patch.object(TokenBackend, 'decode')
    def test_add_step_to_recipe(self, mock_decode):
        """
        Testing add_step_to_recipe properly
        adds a step to a user's recipe.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(
                f'{API_VERSION}:recipe_steps',
                kwargs={'recipe_name': self.recipe.recipe_name},
            ),
            json.dumps({'step': self.step1}),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe.recipe_name,
                'steps': [self.step1],
                'ingredients': []
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_add_step_to_nonexistant_recipe(self, mock_decode):
        """
        Testing add_step_to_recipe works properly
        when given a non-existant recipe.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(
                f'{API_VERSION}:recipe_steps',
                kwargs={'recipe_name': 'doesnt_exist'},
            ),
            json.dumps({'step': self.step1}),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 404)

    @patch.object(TokenBackend, 'decode')
    def test_edit_step_in_recipe(self, mock_decode):
        """
        Testing edit_step_in_recipe properly
        edits a step from a user's recipe.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(
                f'{API_VERSION}:recipe_steps',
                kwargs={'recipe_name': self.recipe2.recipe_name},
            ),
            json.dumps(
                {
                    'step': self.step2,
                    'step_number': len(self.recipe2.steps)
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe2.recipe_name,
                'steps': [self.step2],
                'ingredients': []
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_edit_step_in_nonexistant_recipe(self, mock_decode):
        """
        Testing edit_step_in_nonexistant_recipe works properly
        when given a non-existant recipe.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(
                f'{API_VERSION}:recipe_steps',
                kwargs={'recipe_name': 'doesnt_exist'},
            ),
            json.dumps(
                {
                    'step': self.step2,
                    'step_number': len(self.recipe2.steps)
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 404)

    @patch.object(TokenBackend, 'decode')
    def test_edit_nonexistant_step_in_recipe(self, mock_decode):
        """
        Testing edit_step_in_nonexistant_recipe works properly
        when given a non-existant step.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(
                f'{API_VERSION}:recipe_steps',
                kwargs={'recipe_name': self.recipe2.recipe_name},
            ),
            json.dumps(
                {
                    'step': self.step2,
                    'step_number': len(self.recipe2.steps) + 1,
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe2.recipe_name,
                'steps': [self.step1],
                'ingredients': []
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_remove_step_from_recipe(self, mock_decode):
        """
        Testing remove_step_from_recipe properly
        removes a step from a user's recipe.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {'step_number': len(self.recipe2.steps)}
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(
                    f'{API_VERSION}:recipe_steps',
                    kwargs={'recipe_name': self.recipe2.recipe_name}
                ),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe2.recipe_name,
                'steps': [],
                'ingredients': []
            }
        )

        # Try removing steps when there are no steps
        query_params = {'step_number': 1}
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(
                    f'{API_VERSION}:recipe_steps',
                    kwargs={'recipe_name': self.recipe2.recipe_name}
                ),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe2.recipe_name,
                'steps': [],
                'ingredients': []
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_remove_nonexistant_step_from_recipe(self, mock_decode):
        """
        Testing remove_step_from_recipe works properly
        when given a non-existant step.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {'step_number': len(self.recipe2.steps) + 1}
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(
                    f'{API_VERSION}:recipe_steps',
                    kwargs={'recipe_name': self.recipe2.recipe_name}
                ),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe2.recipe_name,
                'steps': [self.step1],
                'ingredients': []
            }
        )


class RecipeIngredientApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.user1 = User.objects.create(
            username=USER_VALID_TOKEN_PAYLOAD.get('sub'),
            email=USER_VALID_TOKEN_PAYLOAD.get(CUPBOARD_EMAIL_CLAIM)
        )
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.cust_ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 5,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        self.list_cust_ing1 = {
            'ingredient_name': self.cust_ing1.name,
            'ingredient_type': self.cust_ing1.type,
            'amount': 5,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        self.recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name='My_Recipe2',
            steps=[],
            ingredients=[]
        )
        self.recipe2 = Recipe.objects.create(
            user=self.user1,
            recipe_name='My_Recipe3',
            steps=[],
            ingredients=[self.list_ing1, self.list_cust_ing1]
        )

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_recipe(self, mock_decode):
        """
        Testing add_ingredient_to_recipe properly
        adds an ingredient to a user's recipe.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(
                f'{API_VERSION}:recipe_ingredients',
                kwargs={'recipe_name': self.recipe.recipe_name},
            ),
            json.dumps(
                {
                    'ingredient': self.list_ing1['ingredient_name'],
                    'amount': self.list_ing1['amount'],
                    'unit': self.list_ing1['unit'],
                    'is_custom_ingredient': self.list_ing1['is_custom_ingredient']
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe.recipe_name,
                'steps': [],
                'ingredients': [self.list_ing1]
            }
        )

        # Try adding to a list with an ingredient already in it
        response = self.client.post(
            reverse(
                f'{API_VERSION}:recipe_ingredients',
                kwargs={'recipe_name': self.recipe.recipe_name},
            ),
            json.dumps(
                {
                    'ingredient': self.list_cust_ing1['ingredient_name'],
                    'amount': self.list_cust_ing1['amount'],
                    'unit': self.list_cust_ing1['unit'],
                    'is_custom_ingredient': self.list_cust_ing1['is_custom_ingredient']
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe.recipe_name,
                'steps': [],
                'ingredients': [self.list_ing1, self.list_cust_ing1]
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_add_nonexistant_ingredient_to_recipe(self, mock_decode):
        """
        Testing add_ingredient_to_recipe works properly
        when given a non-existant ingredient.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(
                f'{API_VERSION}:recipe_ingredients',
                kwargs={'recipe_name': self.recipe.recipe_name},
            ),
            json.dumps(
                {
                    'ingredient': 'doesnt_exist',
                    'amount': self.list_ing1['amount'],
                    'unit': self.list_ing1['unit'],
                    'is_custom_ingredient': self.list_ing1['is_custom_ingredient']
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {'message': f'Ingredient {DOES_NOT_EXIST}'}
        )

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_recipe(self, mock_decode):
        """
        Testing remove_ingredient_from_recipe properly
        removes an ingredient from a user's recipe
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {
            'ingredient': self.list_cust_ing1['ingredient_name'],
            'unit': self.list_cust_ing1['unit'],
            'is_custom_ingredient': self.list_cust_ing1['is_custom_ingredient']
        }
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(
                    f'{API_VERSION}:recipe_ingredients',
                    kwargs={'recipe_name': self.recipe2.recipe_name},
                ),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe2.recipe_name,
                'steps': [],
                'ingredients': [self.list_ing1]
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_remove_nonexistant_ingredient_from_recipe(self, mock_decode):
        """
        Testing remove_ingredient_from_recipe works properly
        when given a non-existant ingredient.
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        query_params = {
            'ingredient': 'doesnt_exist',
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        response = self.client.delete(
            '{base_url}?{query_string}'.format(
                base_url=reverse(
                    f'{API_VERSION}:recipe_ingredients',
                    kwargs={'recipe_name': self.recipe2.recipe_name},
                ),
                query_string=urlencode(query_params)
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'user': self.user1.username,
                'recipe_name': self.recipe2.recipe_name,
                'steps': [],
                'ingredients': [self.list_ing1, self.list_cust_ing1]
            }
        )
