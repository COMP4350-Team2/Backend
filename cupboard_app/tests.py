import os
import json

from django.test import TestCase

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
    ADD_ACTION,
    REMOVE_ACTION
)

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')


class IngredientsQueries(TestCase):
    def setUp(self):
        Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        Ingredient.objects.create(name='test_ingredient2', type='test_type1')

    def test_create_ingredient(self):
        """
        Testing create_ingredient creates an ingredient
        in the database
        """
        create_ingredient('test_ingredient3', 'test_type2')
        self.assertEqual(
            Ingredient.objects.filter(
                name='test_ingredient3',
                type='test_type2'
            ).exists(),
            True
        )

    def test_get_all_ingredients(self):
        """
        Testing get_all_ingredients retrieves all the ingredients
        from the database
        """
        ingredients_list = get_all_ingredients()
        self.assertEqual(len(ingredients_list), 2)
        self.assertEqual(
            json.dumps({'name': 'test_ingredient1', 'type': 'test_type1'}),
            str(ingredients_list[0])
        )
        self.assertEqual(
            json.dumps({'name': 'test_ingredient2', 'type': 'test_type1'}),
            str(ingredients_list[1])
        )

    def test_get_ingredient(self):
        """
        Testing get_ingredient returns an ingredient
        from the database
        """
        test_ingredient = get_ingredient('test_ingredient1')
        temp_ingredient = Ingredient.objects.get(name='test_ingredient2')
        test_ingredient2 = get_ingredient('test_ingredient2', temp_ingredient.id)
        test_ingredient3 = get_ingredient('doesnt_exist')

        self.assertEqual(test_ingredient, Ingredient.objects.get(name='test_ingredient1'))
        self.assertEqual(test_ingredient2, Ingredient.objects.get(name='test_ingredient2'))
        self.assertEqual(test_ingredient3, None)


class ListNameQueries(TestCase):
    def test_create_list_name(self):
        """
        Testing create_list creates a list
        in the database
        """
        create_list_name('test_listname1')
        self.assertEqual(ListName.objects.filter(list_name='test_listname1').exists(), True)

    def test_get_all_list_names(self):
        """
        Testing get_all_list_names retrieves all list_names
        in the database
        """
        create_list_name('test_listname1')
        create_list_name('test_listname2')
        create_list_name('test_listname3')
        all_lists = get_all_list_names()
        self.assertEqual(len(all_lists), 3)
        self.assertEqual('test_listname1', str(all_lists[0]))
        self.assertEqual('test_listname2', str(all_lists[1]))
        self.assertEqual('test_listname3', str(all_lists[2]))

    def test_get_list_name(self):
        """
        Testing get_list_name returns an ingredient
        from the database
        """
        create_list_name('test_listname1')
        create_list_name('test_listname2')
        test_list = get_list_name('test_listname1')
        temp_list = ListName.objects.get(list_name='test_listname2')
        test_list2 = get_list_name('test_ingredient2', temp_list.id)
        test_list3 = get_list_name('doesnt_exist')

        self.assertEqual(test_list, ListName.objects.get(list_name='test_listname1'))
        self.assertEqual(test_list2, ListName.objects.get(list_name='test_listname2'))
        self.assertEqual(test_list3, None)


class MeasurementQueries(TestCase):
    def test_create_measurement(self):
        """
        Testing create_measurement creates a measurement
        in the database
        """
        create_measurement('test_unit1')
        self.assertEqual(Measurement.objects.filter(unit='test_unit1').exists(), True)
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
        create_measurement('test_unit1')
        create_measurement('test_unit2')
        create_measurement('test_unit3')
        all_units = get_all_measurements()
        self.assertEqual(len(all_units), 3)
        self.assertEqual('test_unit1', str(all_units[0]))
        self.assertEqual('test_unit2', str(all_units[1]))
        self.assertEqual('test_unit3', str(all_units[2]))

    def test_get_measurement(self):
        """
        Testing get_measurement retrieves a specific measurement
        from the database
        """
        create_measurement('test_unit1')
        create_measurement('test_unit2')
        test_unit = get_measurement('test_unit1')
        temp_unit = Measurement.objects.get(unit='test_unit2')
        test_unit2 = get_measurement('test_unit2', temp_unit.id)
        test_unit3 = get_measurement('doesnt_exist')

        self.assertEqual(test_unit, Measurement.objects.get(unit='test_unit1'))
        self.assertEqual(test_unit2, Measurement.objects.get(unit='test_unit2'))
        self.assertEqual(test_unit3, None)


class UserQueries(TestCase):
    def test_create_user(self):
        """
        Testing create_user creates a measurement
        in the database
        """
        create_user('test_user1', 'user1@test.com')
        self.assertEqual(
            User.objects.filter(
                username='test_user1',
                email='user1@test.com'
            ).exists(),
            True
        )

    def test_get_all_users(self):
        """
        Testing get_all_users retrieves all the users
        from the database
        """
        create_user('test_user1', 'user1@test.com')
        create_user('test_user2', 'user2@test.com')
        create_user('test_user3', 'user3@test.com')
        all_users = get_all_users()
        self.assertEqual(len(all_users), 3)
        self.assertEqual(
            json.dumps({'username': 'test_user1', 'email': 'user1@test.com'}),
            str(all_users[0])
        )
        self.assertEqual(
            json.dumps({'username': 'test_user2', 'email': 'user2@test.com'}),
            str(all_users[1])
        )
        self.assertEqual(
            json.dumps({'username': 'test_user3', 'email': 'user3@test.com'}),
            str(all_users[2])
        )

    def test_get_user(self):
        """
        Testing get_user retrieves the specified user
        from the database
        """
        create_user('test_user1', 'user1@test.com')
        create_user('test_user2', 'user2@test.com')
        test_user = get_user('test_user1')
        temp_user = User.objects.get(username='test_user2')
        test_user2 = get_user('test_user2', temp_user.id)
        test_user3 = get_user('doesnt_exist')

        self.assertEqual(test_user, User.objects.get(username='test_user1'))
        self.assertEqual(test_user2, User.objects.get(username='test_user2'))
        self.assertEqual(test_user3, None)


class UserListIngredientsQueries(TestCase):
    def test_create_list_ingredient(self):
        """
        Testing create_list_ingredient creates an ingredient dictionary
        """
        create_ingredient('test_ingredient1', 'test_type1')
        create_ingredient('test_ingredient2', 'test_type2')
        create_measurement('test_unit1')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        self.assertEqual(
            ing1,
            {
                'ingredient_id': ing1.get('ingredient_id'),
                'ingredient_name': ing1.get('ingredient_name'),
                'amount': 500,
                'unit_id': ing1.get('unit_id'),
                'unit': ing1.get('unit')
            }
        )
        with self.assertRaises(Measurement.DoesNotExist):
            create_list_ingredient('test_ingredient2', 500, 'none')

        with self.assertRaises(ValueError):
            create_list_ingredient('test_ingredient2', 'none', 'test_unit1')

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient('none', 500, 'test_unit1')

    def test_create_user_list_ingredients(self):
        """
        Testing create_user_list_ingredients creates a user list
        """
        create_user('test_user1', 'user1@test.com')
        test_user = get_user('test_user1')

        create_ingredient('test_ingredient1', 'test_type1')
        create_ingredient('test_ingredient2', 'test_type2')
        create_measurement('test_unit1')
        create_measurement('test_unit2')
        create_measurement('test_unit3')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        ing2 = create_list_ingredient('test_ingredient2', 400, 'test_unit2')
        ing_list = []
        ing_list.append(ing1)
        ing_list.append(ing2)

        create_list_name('test_listname1')
        create_user_list_ingredients(test_user.username, 'test_listname1', ing_list)
        list = get_user_lists_ingredients(test_user.username, test_user.id)

        self.assertEqual(list[0].ingredients[0]['ingredient_id'], ing1.get('ingredient_id'))
        self.assertEqual(list[0].ingredients[0]['ingredient_name'], ing1.get('ingredient_name'))
        self.assertEqual(list[0].ingredients[0]['amount'], ing1.get('amount'))
        self.assertEqual(list[0].ingredients[0]['unit_id'], ing1.get('unit_id'))
        self.assertEqual(list[0].ingredients[0]['unit'], ing1.get('unit'))

        self.assertEqual(list[0].ingredients[1]['ingredient_id'], ing2.get('ingredient_id'))
        self.assertEqual(list[0].ingredients[1]['ingredient_name'], ing2.get('ingredient_name'))
        self.assertEqual(list[0].ingredients[1]['amount'], ing2.get('amount'))
        self.assertEqual(list[0].ingredients[1]['unit_id'], ing2.get('unit_id'))
        self.assertEqual(list[0].ingredients[1]['unit'], ing2.get('unit'))

        self.assertEqual(list[0].user.username, 'test_user1')
        self.assertEqual(list[0].user.email, 'user1@test.com')
        self.assertEqual(str(list[0].list_name), 'test_listname1')

        create_list_name('empty_listname1')
        empty_ing = []
        create_user_list_ingredients(test_user.username, 'empty_listname1', empty_ing)

        create_list_name('empty_listname2')
        create_user_list_ingredients(test_user.username, 'empty_listname2', None)

        self.assertEqual(len(list[1].ingredients), 0)
        self.assertEqual(list[1].user.username, 'test_user1')
        self.assertEqual(list[1].user.email, 'user1@test.com')
        self.assertEqual(str(list[1].list_name), 'empty_listname1')

        self.assertEqual(list[2].ingredients, None)
        self.assertEqual(list[2].user.username, 'test_user1')
        self.assertEqual(list[2].user.email, 'user1@test.com')
        self.assertEqual(str(list[2].list_name), 'empty_listname2')

    def test_get_user_lists_ingredients(self):
        """
        Testing get_user_lists_ingredients returns all lists from a user
        """
        create_user('test_user1', 'user1@test.com')
        test_user = get_user('test_user1')

        create_ingredient('test_ingredient1', 'test_type1')
        create_measurement('test_unit1')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        create_list_name('test_listname1')
        create_user_list_ingredients('test_user1', 'test_listname1', ing1)
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
        create_user('test_user1', 'user1@test.com')
        test_user = get_user('test_user1')

        create_ingredient('test_ingredient1', 'test_type1')
        create_ingredient('test_ingredient2', 'test_type2')
        create_measurement('test_unit1')
        create_measurement('test_unit2')
        create_measurement('test_unit3')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        ing2 = create_list_ingredient('test_ingredient2', 400, 'test_unit2')

        # Invalid cases
        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, None, None),

        with self.assertRaises(Measurement.DoesNotExist):
            create_list_ingredient('test_ingredient2', None, None),

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, 400, None),

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, None, 'test_unit2'),

        ing_list = []
        ing_list.append(ing1)
        ing_list.append(ing2)

        create_list_name('test_listname1')
        create_user_list_ingredients('test_user1', 'test_listname1', ing_list)
        get_user_lists_ingredients(test_user.username, test_user.id)

        update_list_ingredient(
            'test_user1',
            'test_listname1',
            'test_ingredient1',
            475,
            'test_unit1',
            REMOVE_ACTION
        )
        update_list_ingredient(
            'test_user1',
            'test_listname1',
            'test_ingredient2',
            300,
            'test_unit3',
            ADD_ACTION
        )
        after = get_user_lists_ingredients(test_user.username, test_user.id)

        self.assertEqual(after[0].ingredients[0]['ingredient_id'], ing1.get('ingredient_id'))
        self.assertEqual(after[0].ingredients[0]['ingredient_name'], ing1.get('ingredient_name'))
        self.assertEqual(after[0].ingredients[0]['amount'], 25)
        self.assertEqual(after[0].ingredients[0]['unit_id'], ing1.get('unit_id'))
        self.assertEqual(after[0].ingredients[0]['unit'], ing1.get('unit'))

        self.assertEqual(after[0].ingredients[1]['ingredient_id'], ing2.get('ingredient_id'))
        self.assertEqual(after[0].ingredients[1]['ingredient_name'], ing2.get('ingredient_name'))
        self.assertEqual(after[0].ingredients[1]['amount'], ing2.get('amount'))
        self.assertEqual(after[0].ingredients[1]['unit_id'], ing2.get('unit_id'))
        self.assertEqual(after[0].ingredients[1]['unit'], ing2.get('unit'))

        self.assertEqual(after[0].ingredients[2]['ingredient_id'], ing2.get('ingredient_id'))
        self.assertEqual(after[0].ingredients[2]['amount'], 300)

        create_list_name('empty_listname1')
        empty_ing = []
        create_user_list_ingredients(test_user.username, 'empty_listname1', empty_ing)
        after = get_user_lists_ingredients(test_user.username, test_user.id)
        update_list_ingredient(
            'test_user1',
            'empty_listname1',
            'test_ingredient1',
            500,
            'test_unit1',
            ADD_ACTION
        )
        self.assertEqual(after[1].ingredients[0]['ingredient_id'], ing1.get('ingredient_id'))
        self.assertEqual(after[1].ingredients[0]['amount'], ing1.get('amount'))
        self.assertEqual(after[1].ingredients[0]['unit_id'], ing1.get('unit_id'))

    def test_remove_list_ingredient(self):
        """
        Testing remove_list_ingredient removes specified ingredient from user's list
        """

        create_user('test_user1', 'user1@test.com')
        create_user('test_user2', 'user2@test.com')
        test_user = get_user('test_user1')
        test_user2 = get_user('test_user2')

        create_ingredient('test_ingredient1', 'test_type1')
        create_ingredient('test_ingredient2', 'test_type2')
        create_measurement('test_unit1')
        create_measurement('test_unit2')
        create_measurement('test_unit3')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        ing2 = create_list_ingredient('test_ingredient2', 400, 'test_unit2')
        ing_list = []
        ing_list.append(ing1)
        ing_list.append(ing2)

        create_list_name('test_listname1')

        create_user_list_ingredients('test_user2', 'test_listname1', None)
        remove_list_ingredient(
            'test_user2',
            'test_listname1',
            ing2.get('ingredient_name'),
            ing2.get('unit')
        )
        list = get_user_lists_ingredients(test_user2.username, test_user2.id)
        self.assertEqual(list[0].ingredients, None)

        create_user_list_ingredients(test_user.username, 'test_listname1', ing_list)
        list = get_user_lists_ingredients(test_user.username, test_user.id)
        remove_list_ingredient(
            'test_user1',
            'test_listname1',
            ing2.get('ingredient_name'),
            ing2.get('unit')
        )

        self.assertEqual(list[0].ingredients[0]['ingredient_id'], ing1.get('ingredient_id'))
        self.assertEqual(list[0].ingredients[0]['ingredient_name'], ing1.get('ingredient_name'))
        self.assertEqual(list[0].ingredients[0]['amount'], ing1.get('amount'))
        self.assertEqual(list[0].ingredients[0]['unit_id'], ing1.get('unit_id'))
        self.assertEqual(list[0].ingredients[0]['unit'], ing1.get('unit'))
        self.assertEqual(len(list[0].ingredients), 1)
