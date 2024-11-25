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
    UserListIngredients,
    CustomIngredient
)
from cupboard_app.queries import (
    DOES_NOT_EXIST,
    GROCERY_LIST_NAME,
    PANTRY_LIST_NAME,
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
                {
                    'message': UserListIngredientsViewSet.MISSING_USER_LIST_PARAM_MSG
                }
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

        self.assertEqual(response.status_code, 500)
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
        self.assertEqual(response.status_code, 500)
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
            'ingredient_id': self.ing1.id,
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 500,
            'unit_id': self.unit1.id,
            'unit': self.unit1.unit
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

        self.assertEqual(response.status_code, 500)
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
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        self.list_ing1 = {
            'ingredient_id': self.ing1.id,
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 5,
            'unit_id': self.unit1.id,
            'unit': self.unit1.unit
        }

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list(self, mock_decode):
        """
        Testing adding an ingredient to an existing list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name1.list_name,
                    'ingredient': self.ing1.name,
                    'amount': self.list_ing1.get('amount'),
                    'unit': self.unit1.unit
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

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_missing_data(self, mock_decode):
        """
        Testing adding an ingredient to an existing list when one
        of the required pieces of information are missing
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:add_set_ingredients'),
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
            {
                'message': UpdateUserListIngredientsViewSet.MISSING_ADD_INGREDIENT_MSG
            }
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'list_name': 'Does not exist',
                    'ingredient': self.ing1.name,
                    'amount': 5,
                    'unit': self.unit1.unit
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 500)
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'list_name': self.list_name1.list_name,
                    'ingredient': 'test_ingredient_fake',
                    'amount': 5,
                    'unit': self.unit1.unit
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 500)
        self.assertDictEqual(
            response.json(),
            {
                'message': f'Ingredient {DOES_NOT_EXIST}'
            }
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
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.unit2 = Measurement.objects.create(unit='test_unit2')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        self.list_ing1 = {
            'ingredient_id': self.ing1.id,
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 50,
            'unit_id': self.unit1.id,
            'unit': self.unit1.unit
        }
        self.list_ing2 = {
            'ingredient_id': self.ing2.id,
            'ingredient_name': self.ing2.name,
            'ingredient_type': self.ing2.type,
            'amount': 50,
            'unit_id': self.unit1.id,
            'unit': self.unit1.unit
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': self.list_ing1.get('ingredient_name'),
                    'old_amount': self.list_ing1.get('amount'),
                    'old_unit': self.list_ing1.get('unit'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': updated_ing1.get('ingredient_name'),
                    'new_amount': updated_ing1.get('amount'),
                    'new_unit': updated_ing1.get('unit')
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': updated_ing1.get('ingredient_name'),
                    'new_amount': updated_ing1.get('amount'),
                    'new_unit': self.unit2.unit
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        updated_ing1 = {
            **updated_ing1,
            'unit_id': self.unit2.id,
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': self.list_ing1.get('ingredient_name'),
                    'new_amount': self.list_ing1.get('amount'),
                    'new_unit': self.list_ing1.get('unit')
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
                {**self.list_ing1, 'unit_id': self.unit2.id, 'unit': self.unit2.unit}
            ]
        )

        response = self.client.patch(
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': list_name3.list_name,
                    'old_ingredient': self.list_ing1.get('ingredient_name'),
                    'old_amount': self.list_ing1.get('amount'),
                    'old_unit': self.unit2.unit,
                    'new_list_name': list_name3.list_name,
                    'new_ingredient': self.list_ing1.get('ingredient_name'),
                    'new_amount': self.list_ing1.get('amount'),
                    'new_unit': self.list_ing1.get('unit'),
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

    @patch.object(TokenBackend, 'decode')
    def test_set_ingredient_not_in_list(self, mock_decode):
        """
        Testing setting an ingredient not in the list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.patch(
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': self.list_ing2.get('ingredient_name'),
                    'old_amount': 0,
                    'old_unit': self.list_ing2.get('unit'),
                    'new_list_name': self.list_name2.list_name,
                    'new_ingredient': self.list_ing2.get('ingredient_name'),
                    'new_amount': self.list_ing2.get('amount'),
                    'new_unit': self.list_ing2.get('unit')
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
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
            {
                'message': UpdateUserListIngredientsViewSet.MISSING_SET_INGREDIENT_MSG
            }
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': 'Does not exist',
                    'old_ingredient': self.list_ing2.get('ingredient_name'),
                    'old_amount': 0,
                    'old_unit': self.list_ing2.get('unit'),
                    'new_list_name': 'Does not exist',
                    'new_ingredient': self.list_ing2.get('ingredient_name'),
                    'new_amount': self.list_ing2.get('amount'),
                    'new_unit': self.list_ing2.get('unit')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 500)
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': self.list_ing2.get('ingredient_name'),
                    'old_amount': 0,
                    'old_unit': self.list_ing2.get('unit'),
                    'new_list_name': self.list_name2.list_name,
                    'new_ingredient': 'Does not exist',
                    'new_amount': self.list_ing2.get('amount'),
                    'new_unit': self.list_ing2.get('unit')
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 500)
        self.assertDictEqual(
            response.json(),
            {
                'message': f'Ingredient {DOES_NOT_EXIST}'
            }
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name1.list_name,
                    'old_ingredient': self.list_ing1.get('ingredient_name'),
                    'old_amount': self.list_ing1.get('amount'),
                    'old_unit': self.list_ing1.get('unit'),
                    'new_list_name': self.list_name2.list_name,
                    'new_ingredient': self.list_ing1.get('ingredient_name'),
                    'new_amount': self.list_ing1.get('amount'),
                    'new_unit': self.list_ing1.get('unit'),
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
            reverse(f'{API_VERSION}:add_set_ingredients'),
            json.dumps(
                {
                    'old_list_name': self.list_name2.list_name,
                    'old_ingredient': updated_ing1.get('ingredient_name'),
                    'old_amount': updated_ing1.get('amount'),
                    'old_unit': updated_ing1.get('unit'),
                    'new_list_name': self.list_name1.list_name,
                    'new_ingredient': updated_ing1.get('ingredient_name'),
                    'new_amount': updated_ing1.get('amount'),
                    'new_unit': updated_ing1.get('unit'),
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


class DeleteIngredientUserListIngredientsApi(TestCase):
    user1 = None
    ing1 = None
    ing2 = None
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
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type2')
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name=GROCERY_LIST_NAME)
        self.list_name2 = ListName.objects.create(list_name=PANTRY_LIST_NAME)
        self.list_ing1 = {
            'ingredient_id': self.ing1.id,
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 5,
            'unit_id': self.unit1.id,
            'unit': self.unit1.unit
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
    def test_remove_ingredient_from_list(self, mock_decode):
        """
        Testing removing an ingredient from an existing list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:delete_ingredient',
                kwargs={
                    'list_name': self.list_name1.list_name,
                    'ingredient': self.ing1.name,
                    'unit': self.unit1.unit
                }
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
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].ingredients, [])
        self.assertEqual(user_lists[1].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_empty_list(self, mock_decode):
        """
        Testing removing an ingredient from an existing list when list is empty
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:delete_ingredient',
                kwargs={
                    'list_name': self.list_name2.list_name,
                    'ingredient': self.ing1.name,
                    'unit': self.unit1.unit
                }
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
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_list_incorrect_list(self, mock_decode):
        """
        Testing removing an ingredient from a list that doesn't exist
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:delete_ingredient',
                kwargs={
                    'list_name': 'Does not exist',
                    'ingredient': self.ing1.name,
                    'unit': self.unit1.unit
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )

        # Ensures correct response given by view response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'message': INVALID_USER_LIST})

        # Ensures the list items have not been changed
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])

    @patch.object(TokenBackend, 'decode')
    def test_remove_ingredient_from_list_nonexisting_ingredient(self, mock_decode):
        """
        Testing removing a nonexisting ingredient from list
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(
                f'{API_VERSION}:delete_ingredient',
                kwargs={
                    'list_name': self.list_name2.list_name,
                    'ingredient': 'nonexisting_ingredient',
                    'unit': self.unit1.unit
                }
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
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(user_lists[0].ingredients, [self.list_ing1])
        self.assertEqual(user_lists[1].ingredients, [])


class GetAllIngredientsApi(TestCase):
    ing1 = None
    ing2 = None

    def setUp(self):
        """
        Sets up a test database with test values
        """
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type2')

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
            [
                {'name': self.ing1.name, 'type': self.ing1.type},
                {'name': self.ing2.name, 'type': self.ing2.type}
            ]
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
            {
                'message': UserViewSet.MISSING_USER_INFO
            }
        )


class CustomIngredientsApi(TestCase):
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

        self.ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )
        self.ing2 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient2',
            type='test_type1'
        )

    @patch.object(TokenBackend, 'decode')
    def test_create_custom_ingredient(self, mock_decode):
        """
        Testing create_custom_ingredient creates a custom ingredient
        in the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:add_delete_customingredient'),
            json.dumps(
                {
                    'username': self.user1.username,
                    'ingredient': 'Beef',
                    'type': 'Meat'
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {'user': self.user1.username, 'name': 'Beef', 'type': 'Meat'}
        )

    @patch.object(TokenBackend, 'decode')
    def test_create_custom_ingredient_nonexistant_user(self, mock_decode):
        """
        Testing create_custom_ingredient works properly when
        a username doesn't exist in a custom ingredient
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse(f'{API_VERSION}:add_delete_customingredient'),
            json.dumps(
                {
                    'username': 'doesnt_exist',
                    'ingredient': 'Beef',
                    'type': 'Meat'
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)

    @patch.object(TokenBackend, 'decode')
    def test_delete_custom_ingredient(self, mock_decode):
        """
        Testing delete_custom_ingredient deletes a custom ingredient
        in the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(f'{API_VERSION}:add_delete_customingredient'),
            json.dumps(
                {
                    'username': self.user1.username,
                    'ingredient': self.ing1.name
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)

    @patch.object(TokenBackend, 'decode')
    def test_delete_nonexistant_custom_ingredient(self, mock_decode):
        """
        Testing delete_custom_ingredient works properly when a custom
        ingredient to be deleted isnt found in the database
        """
        mock_decode.return_value = USER_VALID_TOKEN_PAYLOAD

        response = self.client.delete(
            reverse(f'{API_VERSION}:add_delete_customingredient'),
            json.dumps(
                {
                    'username': 'doesnt_exist',
                    'ingredient': 'doesnt_exist'
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        self.assertEqual(response.status_code, 200)
