import os
import json
from time import time
from unittest.mock import patch

from django.test import TestCase
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
    create_ingredient,
    get_all_ingredients,
    get_ingredient,
    create_list_name,
    get_all_list_names,
    get_list_name,
    create_measurement,
    get_all_measurements,
    get_measurement,
    create_user,
    get_all_users,
    get_user,
    create_list_ingredient,
    get_user_lists_ingredients,
    create_user_list_ingredients,
    update_list_ingredient,
    remove_list_ingredient,
    UPDATE_FAILED_MSG,
    DOES_NOT_EXIST_MSG,
    CREATE_SUCCESS_MSG,
    EXISTS_MSG
)

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')

# Test payload
VALID_PAYLOAD_TYPE = 'valid'
INVALID_PAYLOAD_TYPE = 'invalid'
TEST_VALID_TOKEN_PAYLOAD = {
    "iss": 'https://{}/'.format(AUTH0_DOMAIN),
    "sub": "CupboardTest@clients",
    "aud": AUTH0_API_IDENTIFIER,
    "iat": time(),
    "exp": time() + 3600,
    "azp": "mK3brgMY0GIMox40xKWcUZBbv2Xs0YdG",
    "scope": "read:messages",
    "gty": "client-credentials",
    "permissions": ["read:messages"],
    "https://cupboard-teacup.com/email": "testing@cupboard.com",
}
TEST_INVALID_TOKEN_PAYLOAD = {
    **TEST_VALID_TOKEN_PAYLOAD,
    "https://cupboard-teacup.com/email": None,
}


# DB Tests
class TestIngredients(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        Ingredient.objects.create(name="test_ingredient1", type="test_type1")
        Ingredient.objects.create(name="test_ingredient2", type="test_type1")

    def test_get_all_ingredients(self):
        """
        Testing get_all_ingredients retrieves all the ingredients
        from the database
        """
        ingredients_list = get_all_ingredients()
        self.assertEqual(len(ingredients_list), 2)
        self.assertEqual(
            json.dumps({"name": "test_ingredient1", "type": "test_type1"}),
            str(ingredients_list[0])
        )
        self.assertEqual(
            json.dumps({"name": "test_ingredient2", "type": "test_type1"}),
            str(ingredients_list[1])
        )

    def test_create_ingredient(self):
        """
        Testing create_ingredient creates an ingredient
        in the database
        """
        create_ingredient("test_ingredient3", "test_type2")
        self.assertEqual(
            Ingredient.objects.filter(
                name="test_ingredient3",
                type="test_type2"
            ).exists(),
            True
        )

    def test_get_ingredient(self):
        """
        Testing get_ingredient returns an ingredient
        from the database
        """
        test_ingredient = get_ingredient("test_ingredient1")
        temp_ingredient = Ingredient.objects.get(name="test_ingredient2")
        test_ingredient2 = get_ingredient("test_ingredient2", temp_ingredient.id)
        test_ingredient3 = get_ingredient("doesnt_exist")

        self.assertEqual(test_ingredient, Ingredient.objects.get(name="test_ingredient1"))
        self.assertEqual(test_ingredient2, Ingredient.objects.get(name="test_ingredient2"))
        self.assertEqual(test_ingredient3, None)

    def test_create_list_name(self):
        """
        Testing create_list creates a list
        in the database
        """
        create_list_name("test_listname")
        self.assertEqual(ListName.objects.filter(list_name="test_listname").exists(), True)

    def test_get_all_list_names(self):
        """
        Testing get_all_list_names retrieves all list_names
        in the database
        """
        create_list_name("test_listname")
        create_list_name("test_listname2")
        create_list_name("test_listname3")
        all_lists = get_all_list_names()
        self.assertEqual(len(all_lists), 3)
        self.assertEqual("test_listname", str(all_lists[0]))
        self.assertEqual("test_listname2", str(all_lists[1]))
        self.assertEqual("test_listname3", str(all_lists[2]))

    def test_get_list_name(self):
        """
        Testing get_list_name returns an ingredient
        from the database
        """
        create_list_name("test_listname")
        create_list_name("test_listname2")
        test_list = get_list_name("test_listname")
        temp_list = ListName.objects.get(list_name="test_listname2")
        test_list2 = get_list_name("test_ingredient2", temp_list.id)
        test_list3 = get_list_name("doesnt_exist")

        self.assertEqual(test_list, ListName.objects.get(list_name="test_listname"))
        self.assertEqual(test_list2, ListName.objects.get(list_name="test_listname2"))
        self.assertEqual(test_list3, None)

    def test_create_measurement(self):
        """
        Testing create_measurement creates a measurement
        in the database
        """
        create_measurement("test_unit")
        self.assertEqual(Measurement.objects.filter(unit="test_unit").exists(), True)
        create_measurement(5)
        self.assertEqual(
            Measurement.objects.filter(unit=5).exists(),
            True
        )

    def test_get_all_measurements(self):
        """
        Testing get_all_measurements retrieves all the measurements
        from the database
        """
        create_measurement("test_unit")
        create_measurement("test_unit2")
        create_measurement("test_unit3")
        all_units = get_all_measurements()
        self.assertEqual(len(all_units), 3)
        self.assertEqual("test_unit", str(all_units[0]))
        self.assertEqual("test_unit2", str(all_units[1]))
        self.assertEqual("test_unit3", str(all_units[2]))

    def test_get_measurement(self):
        """
        Testing get_measurement retrieves a specific measurement
        from the database
        """
        create_measurement("test_unit")
        create_measurement("test_unit2")
        test_unit = get_measurement("test_unit")
        temp_unit = Measurement.objects.get(unit="test_unit2")
        test_unit2 = get_measurement("test_unit2", temp_unit.id)
        test_unit3 = get_measurement("doesnt_exist")

        self.assertEqual(test_unit, Measurement.objects.get(unit="test_unit"))
        self.assertEqual(test_unit2, Measurement.objects.get(unit="test_unit2"))
        self.assertEqual(test_unit3, None)

    def test_create_user(self):
        """
        Testing create_user creates a measurement
        in the database
        """
        create_user("test_user", "user@test.com")
        self.assertEqual(
            User.objects.filter(
                username="test_user",
                email="user@test.com"
            ).exists(),
            True
        )

    def test_get_all_users(self):
        """
        Testing get_all_users retrieves all the users
        from the database
        """
        create_user("test_user", "user@test.com")
        create_user("test_user2", "user2@test.com")
        create_user("test_user3", "user3@test.com")
        all_users = get_all_users()
        self.assertEqual(len(all_users), 3)
        self.assertEqual(
            json.dumps({"username": "test_user", "email": "user@test.com"}),
            str(all_users[0])
        )
        self.assertEqual(
            json.dumps({"username": "test_user2", "email": "user2@test.com"}),
            str(all_users[1])
        )
        self.assertEqual(
            json.dumps({"username": "test_user3", "email": "user3@test.com"}),
            str(all_users[2])
        )

    def test_get_user(self):
        """
        Testing get_user retrieves the specified user
        from the database
        """
        create_user("test_user", "user@test.com")
        create_user("test_user2", "user2@test.com")
        test_user = get_user("test_user")
        temp_user = User.objects.get(username="test_user2")
        test_user2 = get_user("test_user2", temp_user.id)
        test_user3 = get_user("doesnt_exist")

        self.assertEqual(test_user, User.objects.get(username="test_user"))
        self.assertEqual(test_user2, User.objects.get(username="test_user2"))
        self.assertEqual(test_user3, None)

    def test_create_list_ingredient(self):
        """
        Testing create_list_ingredient creates an ingredient dictionary
        """
        create_ingredient("test_ing", "test_type1")
        create_ingredient("test_ing2", "test_type2")
        create_measurement("test_unit")
        ing1 = create_list_ingredient("test_ing", 500, "test_unit")
        ing2 = create_list_ingredient("test_ing2", 500, "none")
        ing3 = create_list_ingredient("test_ing2", "none", "test_unit")
        ing4 = create_list_ingredient("none", 500, "test_unit")
        self.assertEqual(
            ing1,
            {
                "ingredient_id": ing1.get("ingredient_id"),
                "amount": 500,
                "unit_id": ing1.get("unit_id")
            }
        )
        self.assertEqual(ing2, None)
        self.assertEqual(ing3, None)
        self.assertEqual(ing4, None)

    def test_get_user_lists_ingredients(self):
        """
        Testing get_user_lists_ingredients returns all lists from a user
        """
        create_user("test_user", "user@test.com")
        test_user = get_user("test_user")

        create_ingredient("test_ing", "test_type1")
        create_measurement("test_unit")
        ing1 = create_list_ingredient("test_ing", 500, "test_unit")
        create_list_name("test_listname")
        create_user_list_ingredients("test_user", "test_listname", ing1)
        result = get_user_lists_ingredients(test_user.username, test_user.id)
        user_lists = []
        for i in result:
            user_lists.append(i)

        result_lists = []
        result_lists.append(UserListIngredients.objects.get(user=test_user.id))

        self.assertEqual(user_lists, result_lists)

    def test_update_list_ingredient(self):
        """
        Testing update_list_ingredient correctly updates an ingredient in a user's list
        """
        create_user("test_user", "user@test.com")
        test_user = get_user("test_user")

        create_ingredient("test_ing", "test_type1")
        create_ingredient("test_ing2", "test_type2")
        create_measurement("test_unit")
        create_measurement("test_unit2")
        create_measurement("test_unit3")
        ing1 = create_list_ingredient("test_ing", 500, "test_unit")
        ing2 = create_list_ingredient("test_ing2", 400, "test_unit2")

        # Invalid cases
        create_list_ingredient(None, None, None)
        create_list_ingredient("test_ing2", None, None)
        create_list_ingredient(None, 400, None)
        create_list_ingredient(None, None, "test_unit2")

        ing_list = []
        ing_list.append(ing1)
        ing_list.append(ing2)

        create_list_name("test_listname")
        create_user_list_ingredients("test_user", "test_listname", ing_list)
        get_user_lists_ingredients(test_user.username, test_user.id)

        update_list_ingredient("test_user", "test_listname", "test_ing", 25, "test_unit")
        update_list_ingredient("test_user", "test_listname", "test_ing2", 300, "test_unit3")
        after = get_user_lists_ingredients(test_user.username, test_user.id)

        self.assertEqual(after[0].ingredients[0]["ingredient_id"], ing1.get("ingredient_id"))
        self.assertEqual(after[0].ingredients[0]["amount"], 25)
        self.assertEqual(after[0].ingredients[0]["unit_id"], ing1.get("unit_id"))

        self.assertEqual(after[0].ingredients[1]["ingredient_id"], ing2.get("ingredient_id"))
        self.assertEqual(after[0].ingredients[1]["amount"], ing2.get("amount"))
        self.assertEqual(after[0].ingredients[1]["unit_id"], ing2.get("unit_id"))

        self.assertEqual(after[0].ingredients[2]["ingredient_id"], ing2.get("ingredient_id"))
        self.assertEqual(after[0].ingredients[2]["amount"], 300)

        create_list_name("empty_listname")
        empty_ing = []
        create_user_list_ingredients(test_user.username, "empty_listname", empty_ing)
        after = get_user_lists_ingredients(test_user.username, test_user.id)
        update_list_ingredient("test_user", "empty_listname", "test_ing", 500, "test_unit")
        self.assertEqual(after[1].ingredients[0]["ingredient_id"], ing1.get("ingredient_id"))
        self.assertEqual(after[1].ingredients[0]["amount"], ing1.get("amount"))
        self.assertEqual(after[1].ingredients[0]["unit_id"], ing1.get("unit_id"))

    def test_create_user_list_ingredients(self):
        """
        Testing create_user_list_ingredients creates a user list
        """
        create_user("test_user", "user@test.com")
        test_user = get_user("test_user")

        create_ingredient("test_ing", "test_type1")
        create_ingredient("test_ing2", "test_type2")
        create_measurement("test_unit")
        create_measurement("test_unit2")
        create_measurement("test_unit3")
        ing1 = create_list_ingredient("test_ing", 500, "test_unit")
        ing2 = create_list_ingredient("test_ing2", 400, "test_unit2")
        ing_list = []
        ing_list.append(ing1)
        ing_list.append(ing2)

        create_list_name("test_listname")
        create_user_list_ingredients(test_user.username, "test_listname", ing_list)
        list = get_user_lists_ingredients(test_user.username, test_user.id)

        self.assertEqual(list[0].ingredients[0]["ingredient_id"], ing1.get("ingredient_id"))
        self.assertEqual(list[0].ingredients[0]["amount"], ing1.get("amount"))
        self.assertEqual(list[0].ingredients[0]["unit_id"], ing1.get("unit_id"))

        self.assertEqual(list[0].ingredients[1]["ingredient_id"], ing2.get("ingredient_id"))
        self.assertEqual(list[0].ingredients[1]["amount"], ing2.get("amount"))
        self.assertEqual(list[0].ingredients[1]["unit_id"], ing2.get("unit_id"))

        self.assertEqual(list[0].user.username, "test_user")
        self.assertEqual(list[0].user.email, "user@test.com")
        self.assertEqual(str(list[0].list_name), "test_listname")

        create_list_name("empty_listname")
        empty_ing = []
        create_user_list_ingredients(test_user.username, "empty_listname", empty_ing)

        create_list_name("empty_listname2")
        create_user_list_ingredients(test_user.username, "empty_listname2", None)

        self.assertEqual(len(list[1].ingredients), 0)
        self.assertEqual(list[1].user.username, "test_user")
        self.assertEqual(list[1].user.email, "user@test.com")
        self.assertEqual(str(list[1].list_name), "empty_listname")

        self.assertEqual(list[2].ingredients, None)
        self.assertEqual(list[2].user.username, "test_user")
        self.assertEqual(list[2].user.email, "user@test.com")
        self.assertEqual(str(list[2].list_name), "empty_listname2")

    def test_remove_list_ingredient(self):
        """
        Testing remove_list_ingredient removes specified ingredient from user's list
        """

        create_user("test_user", "user@test.com")
        test_user = get_user("test_user")

        create_ingredient("test_ing", "test_type1")
        create_ingredient("test_ing2", "test_type2")
        create_measurement("test_unit")
        create_measurement("test_unit2")
        create_measurement("test_unit3")
        ing1 = create_list_ingredient("test_ing", 500, "test_unit")
        ing2 = create_list_ingredient("test_ing2", 400, "test_unit2")
        ing_list = []
        ing_list.append(ing1)
        ing_list.append(ing2)

        create_list_name("test_listname")
        create_user_list_ingredients(test_user.username, "test_listname", ing_list)
        list = get_user_lists_ingredients(test_user.username, test_user.id)
        remove_list_ingredient("test_user", "test_listname", ing2.get("ingredient_id"))

        self.assertEqual(list[0].ingredients[0]["ingredient_id"], ing1.get("ingredient_id"))
        self.assertEqual(list[0].ingredients[0]["amount"], ing1.get("amount"))
        self.assertEqual(list[0].ingredients[0]["unit_id"], ing1.get("unit_id"))
        self.assertEqual(len(list[0].ingredients), 1)


# API Tests
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
                'message': (
                    'Hello from a public endpoint! '
                    'You don\'t need to be authenticated to see this.'
                )
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
            response.json(), {'message': 'Authentication credentials were not provided.'}
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
            response.json(), {'message': "Given token not valid for any token type"}
        )

    @patch.object(TokenBackend, 'decode')
    def test_private_api_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the private API with a valid token
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse('private'),
            HTTP_AUTHORIZATION="Bearer valid-token"
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
        Testing the private_scoped API without a token
        """
        response = self.client.get(reverse('private_scoped'))
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), {'message': 'Authentication credentials were not provided.'}
        )

    def test_private_scoped_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the private_scoped API with a invalid token
        """
        response = self.client.get(
            reverse('private_scoped'),
            HTTP_AUTHORIZATION="Bearer invalid-token"
        )
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), {'message': "Given token not valid for any token type"}
        )

    @patch.object(TokenBackend, 'decode')
    def test_private_scoped_api_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the private_scoped API with a valid token
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse('private_scoped'),
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': (
                    'Hello from a private endpoint! '
                    'You need to be authenticated and have a permission of '
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

    @patch.object(TokenBackend, 'decode')
    def test_get_all_ingredients(self, mock_decode):
        """
        Testing get_all_ingredients retrieves all the ingredients
        from the database
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.get(
            reverse('get_all_ingredients'),
            HTTP_AUTHORIZATION="Bearer valid-token"
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


class AddIngredientToListApi(TestCase):
    def setUp(self):
        """
        Sets up a test database with test values
        """
        User.objects.create(username="testuser", email="test@test.com")
        ListName.objects.create(list_name="testlist")
        create_ingredient("test_ing", "test_type")
        create_measurement("test_unit")
        UserListIngredients.objects.create(
            user=User.objects.get(username="testuser"),
            list_name=ListName.objects.get(list_name="testlist"),
            ingredients=[]
        )
        Ingredient.objects.create(name="testing2", type="TEST2")

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list(self, mock_decode):
        """
        Testing adding an ingredient to an existing list
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'username': 'testuser',
                    'list_name': 'testlist',
                    'ingredient': 'test_ing',
                    'amount': 5,
                    'unit': 'test_unit'
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )

        self.assertEqual(response.status_code, 200)
        # ensures correct response given by view response
        self.assertDictEqual(
            response.json(),
            {
                'message': 'Item updated successfully.'
            }
        )
        # ensures the item was actually added to the list
        modified_list = UserListIngredients.objects.filter(
            user__username="testuser",
            list_name__list_name="testlist"
        ).first()
        self.assertEqual(
            [{'amount': 5, 'ingredient_id': 1, 'unit_id': 1}],
            modified_list.ingredients
        )

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_missing_data(self, mock_decode):
        """
        Testing adding an ingredient to an existing list when one
        of the required pieces of information are missing
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'list_name': 'testlist',
                    'ingredient': 'test_ing',
                    'amount': 5,
                    'unit': 'test_unit'
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )

        self.assertEqual(response.status_code, 405)
        # ensures correct response given by view response
        # msg created to follow flake8 format
        result = "Required value missing from sent request, "
        result += "please ensure all items are sent in the following format: "
        result += "{username: [USERNAME], list_name: [LISTNAME], ingredient: "
        result += "[INGREDIENT], amount: [AMOUNT/QUANTITY], unit: [MEASURMENT UNIT]}"
        self.assertDictEqual(
            response.json(),
            {
                'message': result
            }
        )

        # ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username="testuser",
            list_name__list_name="testlist"
        ).first()
        self.assertEqual([], modified_list.ingredients)

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_incorect_data(self, mock_decode):
        """
        Testing adding an ingredient to an existing list with an
        incorrect value (ie user that does not actually exist)
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'username': 'testuser_invalid',
                    'list_name': 'testlist',
                    'ingredient': 'test_ing',
                    'amount': 5,
                    'unit': 'test_unit'
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )

        self.assertEqual(response.status_code, 200)
        # ensures correct response given by view response
        self.assertDictEqual(
            response.json(),
            {
                'message': DOES_NOT_EXIST_MSG
            }
        )
        # ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username="testuser",
            list_name__list_name="testlist"
        ).first()
        self.assertEqual([], modified_list.ingredients)

    @patch.object(TokenBackend, 'decode')
    def test_add_ingredient_to_list_nonexisting_ing(self, mock_decode):
        """
        Testing adding an ingredient to an existing list with an ingredient
        that does not acutally exist
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.put(
            reverse('user_list_ingredients'),
            json.dumps(
                {
                    'username': 'testuser',
                    'list_name': 'testlist',
                    'ingredient': 'test_ing_fake',
                    'amount': 5,
                    'unit': 'test_unit'
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )

        self.assertEqual(response.status_code, 200)
        # ensures correct response given by view response
        self.assertDictEqual(
            response.json(),
            {
                'message': f'{UPDATE_FAILED_MSG} Ingredient does not exist.'
            }
        )
        # ensures the list items have not been changed
        modified_list = UserListIngredients.objects.filter(
            user__username="testuser", list_name__list_name="testlist"
        ).first()
        self.assertEqual([], modified_list.ingredients)


class CreateUser(TestCase):
    def test_create_user_without_token_returns_unauthorized(self):
        """
        Testing the create user api without a token
        """
        response = self.client.post(reverse('user'))
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), {'message': 'Authentication credentials were not provided.'}
        )

    def test_create_user_api_with_invalid_token_returns_unauthorized(self):
        """
        Testing the create user api with a invalid token
        """
        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            response.json(), {'message': "Given token not valid for any token type"}
        )

    @patch.object(TokenBackend, 'decode')
    def test_create_user_api_with_valid_token_returns_ok(self, mock_decode):
        """
        Testing the create user api with a valid token.
        We run the same request twice to check response when user already
        exists in the db.
        """
        mock_decode.return_value = TEST_VALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION="Bearer valid-token"
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': CREATE_SUCCESS_MSG
            }
        )

        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION="Bearer valid-token"
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'message': EXISTS_MSG
            }
        )

    @patch.object(TokenBackend, 'decode')
    def test_create_user_api_without_email_token_returns_500(self, mock_decode):
        """
        Testing the create user api with a valid token that does not contain email.
        """
        mock_decode.return_value = TEST_INVALID_TOKEN_PAYLOAD

        response = self.client.post(
            reverse('user'),
            HTTP_AUTHORIZATION="Bearer valid-token"
        )

        self.assertEqual(response.status_code, 500)
        self.assertDictEqual(
            response.json(),
            {
                'message': 'Username or email missing. Unable to create new user.'
            }
        )
