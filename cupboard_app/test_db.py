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
    delete_list_ingredient,
    add_list_ingredient,
    set_list_ingredient,
    create_user_list_ingredients,
    delete_user_list_ingredients,
    get_user_lists_ingredients,
    get_specific_user_lists_ingredients,
    change_user_list_ingredient_name,
    add_default_user_lists,
    GROCERY_LIST_NAME,
    PANTRY_LIST_NAME
)


class IngredientsQueries(TestCase):
    def setUp(self):
        Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        Ingredient.objects.create(name='test_ingredient2', type='test_type1')

    def test_create_ingredient(self):
        """
        Testing create_ingredient creates an ingredient in the database
        """
        create_ingredient('test_ingredient3', 'test_type2')
        self.assertEqual(
            Ingredient.objects.filter(name='test_ingredient3', type='test_type2').exists(),
            True
        )

    def test_get_all_ingredients(self):
        """
        Testing get_all_ingredients retrieves all the ingredients from the database
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
        Testing get_ingredient returns an ingredient from the database
        """
        test_ingredient = get_ingredient('test_ingredient1')
        temp_ingredient = Ingredient.objects.get(name='test_ingredient2')
        test_ingredient2 = get_ingredient('test_ingredient2', temp_ingredient.id)
        test_ingredient3 = get_ingredient('doesnt_exist')

        self.assertEqual(test_ingredient, Ingredient.objects.get(name='test_ingredient1'))
        self.assertEqual(test_ingredient2, Ingredient.objects.get(name='test_ingredient2'))
        self.assertEqual(test_ingredient3, None)


class ListNameQueries(TestCase):
    def setUp(self):
        ListName.objects.create(list_name='test_listname1')
        ListName.objects.create(list_name='test_listname2')

    def test_create_list_name(self):
        """
        Testing create_list creates a list in the database
        """
        create_list_name('test_listname3')
        self.assertEqual(
            ListName.objects.filter(list_name='test_listname3').exists(),
            True
        )

    def test_get_all_list_names(self):
        """
        Testing get_all_list_names retrieves all list_names in the database
        """
        all_lists = get_all_list_names()
        self.assertEqual(len(all_lists), 2)
        self.assertEqual(str(all_lists[0]), 'test_listname1')
        self.assertEqual(str(all_lists[1]), 'test_listname2')

    def test_get_list_name(self):
        """
        Testing get_list_name returns an ingredient from the database
        """
        test_list = get_list_name('test_listname1')
        temp_list = ListName.objects.get(list_name='test_listname2')
        test_list2 = get_list_name('test_ingredient2', temp_list.id)
        test_list3 = get_list_name('doesnt_exist')

        self.assertEqual(test_list, ListName.objects.get(list_name='test_listname1'))
        self.assertEqual(test_list2, ListName.objects.get(list_name='test_listname2'))
        self.assertEqual(test_list3, None)


class MeasurementQueries(TestCase):
    def setUp(self):
        Measurement.objects.create(unit='test_unit1')
        Measurement.objects.create(unit='test_unit2')

    def test_create_measurement(self):
        """
        Testing create_measurement creates a measurement in the database
        """
        create_measurement('test_unit3')
        self.assertEqual(Measurement.objects.filter(unit='test_unit3').exists(), True)

        create_measurement(5)
        self.assertEqual(Measurement.objects.filter(unit=5).exists(), True)

    def test_get_all_measurements(self):
        """
        Testing get_all_measurements retrieves all the measurements from the database
        """
        all_units = get_all_measurements()
        self.assertEqual(len(all_units), 2)
        self.assertEqual(str(all_units[0]), 'test_unit1')
        self.assertEqual(str(all_units[0]), 'test_unit2')

    def test_get_measurement(self):
        """
        Testing get_measurement retrieves a specific measurement from the database
        """
        test_unit = get_measurement('test_unit1')
        temp_unit = Measurement.objects.get(unit='test_unit2')
        test_unit2 = get_measurement('test_unit2', temp_unit.id)
        test_unit3 = get_measurement('doesnt_exist')

        self.assertEqual(test_unit, Measurement.objects.get(unit='test_unit1'))
        self.assertEqual(test_unit2, Measurement.objects.get(unit='test_unit2'))
        self.assertEqual(test_unit3, None)


class UserQueries(TestCase):
    def setUp(self):
        User.objects.create(username='test_user1', email='user1@test.com')
        User.objects.create(username='test_user2', email='user2@test.com')

    def test_create_user(self):
        """
        Testing create_user creates a measurement in the database
        """
        create_user('test_user3', 'user3@test.com')
        self.assertEqual(
            User.objects.filter(
                username='test_user3',
                email='user3@test.com'
            ).exists(),
            True
        )

    def test_get_all_users(self):
        """
        Testing get_all_users retrieves all the users from the database
        """
        all_users = get_all_users()
        self.assertEqual(len(all_users), 2)
        self.assertEqual(
            json.dumps({'username': 'test_user1', 'email': 'user1@test.com'}),
            str(all_users[0])
        )
        self.assertEqual(
            json.dumps({'username': 'test_user2', 'email': 'user2@test.com'}),
            str(all_users[1])
        )

    def test_get_user(self):
        """
        Testing get_user retrieves the specified user from the database
        """
        test_user = get_user('test_user1')
        temp_user = User.objects.get(username='test_user2')
        test_user2 = get_user('test_user2', temp_user.id)
        test_user3 = get_user('doesnt_exist')

        self.assertEqual(test_user, User.objects.get(username='test_user1'))
        self.assertEqual(test_user2, User.objects.get(username='test_user2'))
        self.assertEqual(test_user3, None)


class UserListIngredientsQueries(TestCase):
    def setUp(self):
        User.objects.create(username='test_user1', email='user1@test.com')
        User.objects.create(username='test_user2', email='user2@test.com')
        Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        Ingredient.objects.create(name='test_ingredient2', type='test_type1')
        ListName.objects.create(list_name='test_listname1')
        ListName.objects.create(list_name='test_listname2')
        ListName.objects.create(list_name='empty_listname1')
        ListName.objects.create(list_name='empty_listname2')
        Measurement.objects.create(unit='test_unit1')
        Measurement.objects.create(unit='test_unit2')
        Measurement.objects.create(unit='test_unit3')

    def test_create_user_list_ingredients(self):
        """
        Testing create_user_list_ingredients creates a user list
        """
        test_user = User.objects.get(username='test_user1')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        ing2 = create_list_ingredient('test_ingredient2', 400, 'test_unit2')
        ing_list = []
        ing_list.append(ing1)
        ing_list.append(ing2)

        create_user_list_ingredients(test_user.username, 'test_listname1', ing_list)
        list = UserListIngredients.objects.filter(user__username='test_user1')

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

        create_user_list_ingredients(test_user.username, 'empty_listname1', [])
        create_user_list_ingredients(test_user.username, 'empty_listname2', None)

        self.assertEqual(len(list[1].ingredients), 0)
        self.assertEqual(list[1].user.username, 'test_user1')
        self.assertEqual(list[1].user.email, 'user1@test.com')
        self.assertEqual(str(list[1].list_name), 'empty_listname1')

        self.assertEqual(list[2].ingredients, None)
        self.assertEqual(list[2].user.username, 'test_user1')
        self.assertEqual(list[2].user.email, 'user1@test.com')
        self.assertEqual(str(list[2].list_name), 'empty_listname2')

    def test_delete_user_list_ingredients(self):
        """
        Testing delete_user_list_ingredients correctly deletes a user's list.
        """
        user1 = User.objects.get('test_user1')
        list_name1 = ListName.objects.get('test_listname1')
        list_name2 = ListName.objects.get('test_listname2')

        UserListIngredients.objects.create(user=user1, listName=list_name1, ingredients=[])
        UserListIngredients.objects.create(user=user1, listName=list_name2, ingredients=[])

        user_lists = UserListIngredients.objects.filter(user__username='test_user1')
        self.assertEqual(user_lists[0].user.username, 'test_user1')
        self.assertEqual(user_lists[0].user.email, 'user1@test.com')
        self.assertEqual(str(user_lists[0].list_name), 'test_listname1')
        self.assertEqual(user_lists[1].user.username, 'test_user1')
        self.assertEqual(user_lists[1].user.email, 'user1@test.com')
        self.assertEqual(str(user_lists[1].list_name), 'test_listname2')

        delete_user_list_ingredients(username='test_user1', list_name='test_listname1')
        delete_user_list_ingredients(username='test_user1', list_name='test_listname2')
        self.assertEqual(user_lists, [])

        delete_user_list_ingredients(username='test_user1', list_name='test_listname1')
        self.assertEqual(user_lists, [])

    def test_get_user_lists_ingredients(self):
        """
        Testing get_user_lists_ingredients returns all lists from a user
        """
        test_user = User.objects.get(username='test_user1')
        list_name = ListName.objects.get(list_name='test_listname1')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        UserListIngredients.objects.create(
            user=test_user,
            list_name=list_name,
            ingredients=[ing1]
        )
        result = get_user_lists_ingredients(test_user.username, test_user.id)
        user_lists = []
        for i in result:
            user_lists.append(i)

        result_lists = []
        result_lists.append(UserListIngredients.objects.get(user=test_user.id))

        self.assertEqual(user_lists, result_lists)

    def test_get_specific_user_lists_ingredients(self):
        """
        Testing get_specific_user_lists_ingredients returns all lists from a user
        """
        test_user = User.objects.get(username='test_user1')
        ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        list_created = create_user_list_ingredients('test_user1', 'test_listname1', ing1)
        result = get_specific_user_lists_ingredients(test_user.username, 'test_listname1')
        self.assertEqual(result, list_created)

    def test_change_user_list_ingredient_name(self):
        """
        Testing change_user_list_ingredient_name returns the list with the name changed
        """
        user1 = User.objects.get('test_user1')
        list_name1 = ListName.objects.get('test_listname1')
        list_ing = create_list_ingredient(ingredient='Beef', amount=500, unit='g')

        UserListIngredients.objects.create(
            user=user1,
            listName=list_name1,
            ingredients=[list_ing]
        )
        change_user_list_ingredient_name(
            username='test_user1',
            old_list_name='test_listname1',
            new_list_name='test_listname2'
        )
        self.assertEqual(
            UserListIngredients.objects.filter(
                user__username='test_user1',
                list_name__list_name='test_listname2'
            ).exists(),
            True
        )
        self.assertEqual(
            UserListIngredients.objects.filter(
                user__username='test_user1',
                list_name__list_name='test_listname2'
            ).first().ingredients,
            [list_ing]
        )

    def test_add_default_user_lists(self):
        """
        Testing add_default_user_lists returns the user lists with Grocery and Pantry added 
        """
        add_default_user_lists(username='test_user1')
        user_lists = UserListIngredients.objects.filter(user__username='test_user1')
        self.assertEqual(user_lists[0].user.username, 'test_user1')
        self.assertEqual(user_lists[0].user.email, 'user1@test.com')
        self.assertEqual(str(user_lists[0].list_name), GROCERY_LIST_NAME)
        self.assertEqual(user_lists[1].user.username, 'test_user1')
        self.assertEqual(user_lists[1].user.email, 'user1@test.com')
        self.assertEqual(str(user_lists[1].list_name), PANTRY_LIST_NAME)

    def test_create_list_ingredient(self):
        """
        Testing create_list_ingredient creates an ingredient dictionary
        """
        ing = Ingredient.objects.get('test_ingredient1')
        unit = Measurement.objects.get('test_unit1')
        list_ing = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        self.assertEqual(
            list_ing,
            {
                'ingredient_id': ing.get('id'),
                'ingredient_name': 'test_ingredient1',
                'amount': 500,
                'unit_id': unit.get('unit_id'),
                'unit': 'test_unit1'
            }
        )
        with self.assertRaises(Measurement.DoesNotExist):
            create_list_ingredient('test_ingredient2', 500, 'none')

        with self.assertRaises(ValueError):
            create_list_ingredient('test_ingredient2', 'none', 'test_unit1')

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient('none', 500, 'test_unit1')

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, None, None)

        with self.assertRaises(Measurement.DoesNotExist):
            create_list_ingredient('test_ingredient2', None, None)

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, 400, None)

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, None, 'test_unit2')

    def test_delete_list_ingredient(self):
        """
        Testing delete_list_ingredient removes specified ingredient from user's list
        """
        test_user = User.objects.get(username='test_user1')
        test_user2 = User.objects.get(username='test_user2')
        list_ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        list_ing2 = create_list_ingredient('test_ingredient2', 400, 'test_unit2')
        ing_list = []
        ing_list.append(list_ing1)
        ing_list.append(list_ing2)

        # Delete when ingredients is empty
        create_user_list_ingredients('test_user2', 'test_listname1', None)
        delete_list_ingredient(
            'test_user2',
            'test_listname1',
            list_ing2.get('ingredient_name'),
            list_ing2.get('unit')
        )
        list = get_user_lists_ingredients('test_user2', test_user2.id)
        self.assertEqual(list[0].ingredients, None)

        # Delete when ingredients contains elements
        create_user_list_ingredients('test_user1', 'test_listname1', ing_list)
        list = get_user_lists_ingredients('test_user1', test_user.id)
        delete_list_ingredient(
            'test_user1',
            'test_listname1',
            list_ing2.get('ingredient_name'),
            list_ing2.get('unit')
        )
        self.assertEqual(len(list[0].ingredients), 1)
        self.assertEqual(
            list[0].ingredients
            [
                {
                    'ingredient_id': list_ing1.get('ingredient_id'),
                    'ingredient_name': 'test_ingredient1',
                    'amount': 500,
                    'unit_id': list_ing1.get('unit_id'),
                    'unit': 'test_unit1'
                }
            ]
        )
'''
    def test_add_list_ingredient(self):
        """
        Testing add_list_ingredient correctly adds an ingredient in a user's list
        """
        test_user = User.objects.get(username='test_user1')
        test_user2 = User.objects.get(username='test_user2')
        list_ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        list_ing2 = create_list_ingredient('test_ingredient2', 400, 'test_unit2')
        ing_list = []
        ing_list.append(list_ing1)
        ing_list.append(list_ing2)

        # Delete when ingredients is empty
        create_user_list_ingredients('test_user2', 'test_listname1', None)


    def test_set_list_ingredient(self):
        """
        Testing set_list_ingredient correctly updates an ingredient in a user's list
        """
        test_user = User.objects.get(username='test_user1')
        list_ing1 = create_list_ingredient('test_ingredient1', 500, 'test_unit1')
        list_ing2 = create_list_ingredient('test_ingredient2', 400, 'test_unit2')
        ing_list = []
        ing_list.append(list_ing1)
        ing_list.append(list_ing2)

        create_list_name('test_listname1')
        create_user_list_ingredients('test_user1', 'test_listname1', ing_list)
        get_user_lists_ingredients(test_user.username, test_user.id)

        set_list_ingredient(
            'test_user1',
            'test_listname1',
            'test_ingredient1',
            25,
            'test_unit1',
            setting=True
        )
        set_list_ingredient(
            'test_user1',
            'test_listname1',
            'test_ingredient2',
            300,
            'test_unit3',
            setting=True
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
        set_list_ingredient(
            'test_user1',
            'empty_listname1',
            'test_ingredient1',
            500,
            'test_unit1',
            setting=True
        )
        self.assertEqual(after[1].ingredients[0]['ingredient_id'], ing1.get('ingredient_id'))
        self.assertEqual(after[1].ingredients[0]['amount'], ing1.get('amount'))
        self.assertEqual(after[1].ingredients[0]['unit_id'], ing1.get('unit_id'))
'''