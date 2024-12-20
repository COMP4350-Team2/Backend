import json

from django.test import TestCase

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
    create_ingredient,
    get_all_ingredients,
    get_ingredient,
    create_custom_ingredient,
    get_all_custom_ingredients,
    get_custom_ingredient,
    delete_custom_ingredient,
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
    create_recipe,
    delete_recipe,
    add_ingredient_to_recipe,
    remove_ingredient_from_recipe,
    add_step_to_recipe,
    remove_step_from_recipe,
    edit_step_in_recipe,
    get_all_recipes,
    get_recipe,
    GROCERY_LIST_NAME,
    PANTRY_LIST_NAME,
    MAX_LISTS
)


class IngredientsQueries(TestCase):
    ing1 = None
    ing2 = None

    def setUp(self):
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type1')

    def test_create_ingredient(self):
        """
        Testing create_ingredient creates an ingredient in the database
        """
        create_ingredient(name='test_ingredient3', type='test_type2')
        self.assertEqual(
            Ingredient.objects.filter(name='test_ingredient3', type='test_type2').exists(),
            True
        )
        self.assertEqual(len(Ingredient.objects.all()), 3)

        create_ingredient(name='test_ingredient3', type='test_type2')
        self.assertEqual(len(Ingredient.objects.all()), 3)

    def test_get_all_ingredients(self):
        """
        Testing get_all_ingredients retrieves all the ingredients from the database
        """
        ingredients_list = get_all_ingredients()
        self.assertEqual(len(ingredients_list), 2)
        self.assertEqual(
            json.dumps({'name': self.ing1.name, 'type': self.ing1.type}),
            str(ingredients_list[0])
        )
        self.assertEqual(
            json.dumps({'name': self.ing2.name, 'type': self.ing2.type}),
            str(ingredients_list[1])
        )

    def test_get_ingredient(self):
        """
        Testing get_ingredient returns an ingredient from the database
        """
        test_ingredient = get_ingredient(name=self.ing1.name)
        test_ingredient2 = get_ingredient(name=self.ing2.name, id=self.ing2.id)
        self.assertEqual(test_ingredient, self.ing1)
        self.assertEqual(test_ingredient2, self.ing2)

        with self.assertRaises(Ingredient.DoesNotExist):
            get_ingredient(name='doesnt_exist')


class CustomIngredientQueries(TestCase):
    user = None
    ing1 = None
    ing2 = None
    unit1 = None
    list_name1 = None
    list_cust_ing1 = None
    list_cust_ing2 = None
    list1 = None

    def setUp(self):
        self.user = User.objects.create(username='test_user', email='test_user@cupboard.app')
        self.ing1 = CustomIngredient.objects.create(
            user=self.user, name='test_ingredient1', type='test_type1'
        )
        self.ing2 = CustomIngredient.objects.create(
            user=self.user, name='test_ingredient2', type='test_type1'
        )
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.list_name1 = ListName.objects.create(list_name='test_listname1')
        self.list_cust_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 500,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        self.list_cust_ing2 = {
            'ingredient_name': self.ing2.name,
            'ingredient_type': self.ing2.type,
            'amount': 400,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        self.list1 = UserListIngredients.objects.create(
            user=self.user,
            list_name=self.list_name1,
            ingredients=[self.list_cust_ing1, self.list_cust_ing2]
        )

    def test_create_custom_ingredient(self):
        """
        Testing create_custom_ingredient creates a custom ingredient for the user
        """
        create_custom_ingredient(username='test_user', name='test_ingredient3', type='test_type2')
        self.assertEqual(
            CustomIngredient.objects.filter(
                user=self.user, name='test_ingredient3', type='test_type2'
            ).exists(),
            True
        )
        self.assertEqual(len(CustomIngredient.objects.all()), 3)

        create_custom_ingredient(username='test_user', name='test_ingredient3', type='test_type2')
        self.assertEqual(len(CustomIngredient.objects.all()), 3)

        # Test creating custom ingredient with same name as a common ingredient
        common_ing1 = Ingredient.objects.create(name='common_ing1', type='test_type1')
        with self.assertRaises(ValueError):
            create_custom_ingredient(
                username='test_user',
                name=common_ing1.name,
                type=common_ing1.type
            )

    def test_get_all_custom_ingredients(self):
        """
        Testing get_all_custom_ingredients retrieves all the custom ingredients for the user
        """
        user2 = User.objects.create(username='test_user2', email='test_user2@cupboard.app')
        ing3 = CustomIngredient.objects.create(
            user=user2, name='test_ingredient3', type='test_type1'
        )
        ingredients_list = get_all_custom_ingredients(self.user.username)
        self.assertEqual(len(ingredients_list), 2)
        self.assertEqual(
            json.dumps({'name': self.ing1.name, 'type': self.ing1.type}),
            str(ingredients_list[0])
        )
        self.assertEqual(
            json.dumps({'name': self.ing2.name, 'type': self.ing2.type}),
            str(ingredients_list[1])
        )

        ingredients_list2 = get_all_custom_ingredients(user2.username)
        self.assertEqual(len(ingredients_list2), 1)
        self.assertEqual(
            json.dumps({'name': ing3.name, 'type': ing3.type}),
            str(ingredients_list2[0])
        )

    def test_get_custom_ingredient(self):
        """
        Testing get_ingredient returns an ingredient from the database
        """
        test_ingredient = get_custom_ingredient(
            username=self.user.username,
            name=self.ing1.name
        )
        test_ingredient2 = get_custom_ingredient(
            username=self.user.username,
            name=self.ing2.name, id=self.ing2.id
        )
        self.assertEqual(test_ingredient, self.ing1)
        self.assertEqual(test_ingredient2, self.ing2)

        with self.assertRaises(CustomIngredient.DoesNotExist):
            get_custom_ingredient(username=self.user.username, name='doesnt_exist')

    def test_delete_custom_ingredient(self):
        """
        Testing delete_custom_ingredient deletes a custom ingredient from the database
        """
        self.assertEqual(len(CustomIngredient.objects.all().filter(user=self.user)), 2)
        list = UserListIngredients.objects.get(user=self.user, list_name=self.list_name1)
        self.assertEqual(len(list.ingredients), 2)

        delete_custom_ingredient(self.user.username, self.ing1.name)
        self.assertEqual(len(CustomIngredient.objects.all().filter(user=self.user)), 1)
        list = UserListIngredients.objects.get(user=self.user, list_name=self.list_name1)
        self.assertEqual(len(list.ingredients), 1)

        delete_custom_ingredient(self.user.username, 'does not exist')
        self.assertEqual(len(CustomIngredient.objects.all().filter(user=self.user)), 1)
        list = UserListIngredients.objects.get(user=self.user, list_name=self.list_name1)
        self.assertEqual(len(list.ingredients), 1)

        with self.assertRaises(User.DoesNotExist):
            delete_custom_ingredient('does not exist', self.ing1.name)

        delete_custom_ingredient(self.user.username, self.ing2.name)
        self.assertEqual(len(CustomIngredient.objects.all().filter(user=self.user)), 0)
        list = UserListIngredients.objects.get(user=self.user, list_name=self.list_name1)
        self.assertEqual(len(list.ingredients), 0)

        self.assertEqual(len(delete_custom_ingredient(self.user.username, self.ing2.name)), 0)
        list = UserListIngredients.objects.get(user=self.user, list_name=self.list_name1)
        self.assertEqual(len(list.ingredients), 0)


class ListNameQueries(TestCase):
    list_name1 = None
    list_name2 = None

    def setUp(self):
        self.list_name1 = ListName.objects.create(list_name='test_listname1')
        self.list_name2 = ListName.objects.create(list_name='test_listname2')

    def test_create_list_name(self):
        """
        Testing create_list creates a list in the database
        """
        create_list_name(list_name='test_listname3')
        self.assertEqual(
            ListName.objects.filter(list_name='test_listname3').exists(),
            True
        )
        self.assertEqual(len(ListName.objects.all()), 3)

        create_list_name(list_name='test_listname3')
        self.assertEqual(len(ListName.objects.all()), 3)

    def test_get_all_list_names(self):
        """
        Testing get_all_list_names retrieves all list_names in the database
        """
        all_lists = get_all_list_names()
        self.assertEqual(len(all_lists), 2)
        self.assertEqual(str(all_lists[0]), self.list_name1.list_name)
        self.assertEqual(str(all_lists[1]), self.list_name2.list_name)

    def test_get_list_name(self):
        """
        Testing get_list_name returns an ingredient from the database
        """
        test_list = get_list_name(list_name=self.list_name1.list_name)
        test_list2 = get_list_name(
            list_name=self.list_name2.list_name,
            id=self.list_name2.id
        )
        self.assertEqual(test_list, self.list_name1)
        self.assertEqual(test_list2, self.list_name2)

        with self.assertRaises(ListName.DoesNotExist):
            get_list_name(list_name='doesnt_exist')


class MeasurementQueries(TestCase):
    unit1 = None
    unit2 = None

    def setUp(self):
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.unit2 = Measurement.objects.create(unit='test_unit2')

    def test_create_measurement(self):
        """
        Testing create_measurement creates a measurement in the database
        """
        create_measurement(unit='test_unit3')
        self.assertEqual(Measurement.objects.filter(unit='test_unit3').exists(), True)

        create_measurement(unit=5)
        self.assertEqual(Measurement.objects.filter(unit=5).exists(), True)
        self.assertEqual(len(Measurement.objects.all()), 4)

        # Try creating same object again
        create_measurement(unit=5)
        self.assertEqual(len(Measurement.objects.all()), 4)

    def test_get_all_measurements(self):
        """
        Testing get_all_measurements retrieves all the measurements from the database
        """
        all_units = get_all_measurements()
        self.assertEqual(len(all_units), 2)
        self.assertEqual(str(all_units[0]), self.unit1.unit)
        self.assertEqual(str(all_units[1]), self.unit2.unit)

    def test_get_measurement(self):
        """
        Testing get_measurement retrieves a specific measurement from the database
        """
        test_unit = get_measurement(unit=self.unit1.unit)
        test_unit2 = get_measurement(unit=self.unit2.unit, id=self.unit2.id)
        self.assertEqual(test_unit, self.unit1)
        self.assertEqual(test_unit2, self.unit2)

        with self.assertRaises(Measurement.DoesNotExist):
            get_measurement(unit='doesnt_exist')


class UserQueries(TestCase):
    user1 = None
    user2 = None

    def setUp(self):
        self.user1 = User.objects.create(username='test_user1', email='user1@test.com')
        self.user2 = User.objects.create(username='test_user2', email='user2@test.com')

    def test_create_user(self):
        """
        Testing create_user creates a measurement in the database
        """
        create_user(username='test_user3', email='user3@test.com')
        self.assertEqual(
            User.objects.filter(username='test_user3', email='user3@test.com').exists(),
            True
        )
        self.assertEqual(len(User.objects.all()), 3)

        # Try creating same object again
        create_user(username='test_user3', email='user3@test.com')
        self.assertEqual(len(User.objects.all()), 3)

    def test_get_all_users(self):
        """
        Testing get_all_users retrieves all the users from the database
        """
        all_users = get_all_users()
        self.assertEqual(len(all_users), 2)
        self.assertEqual(
            json.dumps({'username': self.user1.username, 'email': self.user1.email}),
            str(all_users[0])
        )
        self.assertEqual(
            json.dumps({'username': self.user2.username, 'email': self.user2.email}),
            str(all_users[1])
        )

    def test_get_user(self):
        """
        Testing get_user retrieves the specified user from the database
        """
        test_user = get_user(username=self.user1.username)
        test_user2 = get_user(username=self.user2.username, id=self.user2.id)
        self.assertEqual(test_user, self.user1)
        self.assertEqual(test_user2, self.user2)

        with self.assertRaises(User.DoesNotExist):
            get_user(username='doesnt_exist')


class UserListIngredientsQueries(TestCase):
    user1 = None
    user2 = None
    ing1 = None
    ing2 = None
    cust_ing1 = None
    cust_ing2 = None
    list_name1 = None
    list_name2 = None
    empty_list_name1 = None
    empty_list_name2 = None
    unit1 = None
    unit2 = None
    unit3 = None
    list_ing1 = None
    list_ing2 = None
    list_cust_ing1 = None
    list_cust_ing2 = None

    def setUp(self):
        self.user1 = User.objects.create(username='test_user1', email='user1@test.com')
        self.user2 = User.objects.create(username='test_user2', email='user2@test.com')
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type1')
        self.cust_ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name='test_ingredient1',
            type='test_type1'
        )
        self.cust_ing2 = CustomIngredient.objects.create(
            user=self.user2,
            name='test_ingredient1',
            type='test_type1'
        )
        self.list_name1 = ListName.objects.create(list_name='test_listname1')
        self.list_name2 = ListName.objects.create(list_name='test_listname2')
        self.empty_list_name1 = ListName.objects.create(list_name='empty_listname1')
        self.empty_list_name2 = ListName.objects.create(list_name='empty_listname2')
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.unit2 = Measurement.objects.create(unit='test_unit2')
        self.unit3 = Measurement.objects.create(unit='test_unit3')
        self.list_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 500,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        self.list_ing2 = {
            'ingredient_name': self.ing2.name,
            'ingredient_type': self.ing2.type,
            'amount': 400,
            'unit': self.unit2.unit,
            'is_custom_ingredient': False
        }
        self.list_cust_ing1 = {
            'ingredient_name': self.cust_ing1.name,
            'ingredient_type': self.cust_ing1.type,
            'amount': 500,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        self.list_cust_ing2 = {
            'ingredient_name': self.cust_ing2.name,
            'ingredient_type': self.cust_ing2.type,
            'amount': 400,
            'unit': self.unit2.unit,
            'is_custom_ingredient': True
        }

    def test_create_user_list_ingredients(self):
        """
        Testing create_user_list_ingredients creates a user list
        """
        ing_list = [self.list_ing1, self.list_ing2]

        create_user_list_ingredients(
            username=self.user1.username,
            list_name=self.list_name1.list_name,
            ingredients=ing_list
        )
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)

        self.assertEqual(user_lists[0].user, self.user1)
        self.assertEqual(user_lists[0].list_name, self.list_name1)
        self.assertEqual(user_lists[0].ingredients, ing_list)

        create_user_list_ingredients(
            username=self.user1.username,
            list_name=self.empty_list_name1.list_name,
            ingredients=[]
        )
        create_user_list_ingredients(
            username=self.user1.username,
            list_name=self.empty_list_name2.list_name,
            ingredients=None
        )
        # Try creating same object again
        create_user_list_ingredients(
            username=self.user1.username,
            list_name=self.empty_list_name1.list_name,
            ingredients=[self.list_ing1]
        )

        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)

        self.assertEqual(len(user_lists), 3)

        self.assertEqual(user_lists[1].user, self.user1)
        self.assertEqual(user_lists[1].list_name, self.empty_list_name1)
        self.assertEqual(len(user_lists[1].ingredients), 0)

        self.assertEqual(user_lists[2].user, self.user1)
        self.assertEqual(user_lists[2].list_name, self.empty_list_name2)
        self.assertEqual(user_lists[2].ingredients, None)

        # Test max user list ingredients creation
        result = UserListIngredients.objects.filter(user__username=self.user1.username)

        for i in range(MAX_LISTS - len(result)):
            ListName.objects.get_or_create(list_name=f'test_max_listname{i}')
            create_user_list_ingredients(
                username=self.user1.username,
                list_name=f'test_max_listname{i}',
                ingredients=[]
            )

        # Check how many lists we have
        result = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(result), MAX_LISTS)

        with self.assertRaises(ValueError):
            ListName.objects.get_or_create(list_name=f'test_max_listname{MAX_LISTS}')
            create_user_list_ingredients(
                username=self.user1.username,
                list_name=f'test_max_listname{MAX_LISTS}',
                ingredients=[]
            )

        # Check how many lists we have
        result = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(result), MAX_LISTS)

    def test_delete_user_list_ingredients(self):
        """
        Testing delete_user_list_ingredients correctly deletes a user's list.
        """
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

        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(user_lists[0].user, self.user1)
        self.assertEqual(user_lists[0].list_name, self.list_name1)
        self.assertEqual(len(user_lists[0].ingredients), 0)

        self.assertEqual(user_lists[1].user, self.user1)
        self.assertEqual(user_lists[1].list_name, self.list_name2)
        self.assertEqual(len(user_lists[1].ingredients), 0)

        delete_user_list_ingredients(
            username=self.user1.username,
            list_name=self.list_name1.list_name
        )
        delete_user_list_ingredients(
            username=self.user1.username,
            list_name=self.list_name2.list_name
        )
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 0)

        delete_user_list_ingredients(
            username=self.user1.username,
            list_name=self.list_name1.list_name
        )
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 0)

    def test_get_user_lists_ingredients(self):
        """
        Testing get_user_lists_ingredients returns all lists from a user
        """
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[self.list_ing1]
        )

        get_lists = get_user_lists_ingredients(username=self.user1.username, id=self.user1.id)
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(list(get_lists), list(user_lists))

    def test_get_specific_user_lists_ingredients(self):
        """
        Testing get_specific_user_lists_ingredients returns all lists from a user
        """
        list_created = UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[self.list_ing1]
        )
        result = get_specific_user_lists_ingredients(
            username=self.user1.username,
            list_name=self.list_name1.list_name
        )
        self.assertEqual(result, list_created)

        # Getting a non-existent list raises error
        with self.assertRaises(UserListIngredients.DoesNotExist):
            get_specific_user_lists_ingredients(
                username=self.user1.username,
                list_name=self.empty_list_name1.list_name
            )

    def test_change_user_list_ingredient_name(self):
        """
        Testing change_user_list_ingredient_name returns the list with the name changed
        """
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[self.list_ing1]
        )
        change_user_list_ingredient_name(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            new_list_name=self.list_name2.list_name
        )

        # Assert old listname doesn't exist anymore and only the new onw with the ingredients exists
        self.assertEqual(
            UserListIngredients.objects.filter(
                user__username=self.user1.username,
                list_name__list_name=self.list_name1.list_name
            ).exists(),
            False
        )
        self.assertEqual(
            UserListIngredients.objects.filter(
                user__username=self.user1.username,
                list_name__list_name=self.list_name2.list_name
            ).exists(),
            True
        )
        self.assertEqual(
            UserListIngredients.objects.filter(
                user__username=self.user1.username,
                list_name__list_name=self.list_name2.list_name
            ).first().ingredients,
            [self.list_ing1]
        )

        # Changing in a non-existent list raises error
        with self.assertRaises(UserListIngredients.DoesNotExist):
            change_user_list_ingredient_name(
                username=self.user1.username,
                old_list_name=self.empty_list_name1.list_name,
                new_list_name=self.list_name2.list_name
            )

    def test_add_default_user_lists(self):
        """
        Testing add_default_user_lists returns the user lists with Grocery and Pantry added
        """
        # Make sure user had no lists beforehand
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 0)

        # Add the default user lists
        add_default_user_lists(username=self.user1.username)
        user_lists = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_lists), 2)
        self.assertEqual(
            UserListIngredients.objects.filter(
                user__username=self.user1.username,
                list_name__list_name=GROCERY_LIST_NAME
            ).exists(),
            True
        )
        self.assertEqual(
            UserListIngredients.objects.filter(
                user__username=self.user1.username,
                list_name__list_name=PANTRY_LIST_NAME
            ).exists(),
            True
        )

    def test_create_list_ingredient(self):
        """
        Testing create_list_ingredient creates an ingredient dictionary
        """
        list_ing = create_list_ingredient(
            ingredient=self.ing1.name,
            amount=500,
            unit=self.unit1.unit
        )
        self.assertEqual(list_ing, self.list_ing1)

        list_ing2 = create_list_ingredient(
            ingredient=self.list_cust_ing1.get('ingredient_name'),
            amount=500,
            unit=self.list_cust_ing1.get('unit'),
            user_id=self.user1.id
        )
        self.assertEqual(list_ing2, self.list_cust_ing1)

        # Testing list ingredient creation with invalid values
        with self.assertRaises(ValueError):
            create_list_ingredient(self.ing1.name, 15000, self.unit1.unit)

        with self.assertRaises(Measurement.DoesNotExist):
            create_list_ingredient(self.ing2.name, 500, 'none')

        with self.assertRaises(ValueError):
            create_list_ingredient(self.ing2.name, 'none', self.unit1.unit)

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient('none', 500, self.unit1.unit)

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, None, None)

        with self.assertRaises(Measurement.DoesNotExist):
            create_list_ingredient(self.ing2.name, None, None)

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, 400, None)

        with self.assertRaises(Ingredient.DoesNotExist):
            create_list_ingredient(None, None, self.unit2.unit)

    def test_delete_list_ingredient(self):
        """
        Testing delete_list_ingredient removes specified ingredient from user's list
        """
        # Delete when ingredients is empty
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        delete_list_ingredient(
            username=self.user1.username,
            list_name=self.list_name1.list_name,
            ingredient=self.list_ing1.get('ingredient_name'),
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(user_list.ingredients, [])

        # Delete when ingredients is None value
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name2,
            ingredients=None
        )
        delete_list_ingredient(
            username=self.user1.username,
            list_name=self.list_name2.list_name,
            ingredient=self.list_ing1.get('ingredient_name'),
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name2)
        self.assertEqual(user_list.ingredients, None)

        # Delete when ingredients contains elements
        ing_list = [self.list_ing1, self.list_ing2]

        UserListIngredients.objects.create(
            user=self.user2,
            list_name=self.list_name1,
            ingredients=ing_list
        )
        user_list = UserListIngredients.objects.get(user=self.user2, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 2)

        delete_list_ingredient(
            username=self.user2.username,
            list_name=self.list_name1.list_name,
            ingredient=self.list_ing1.get('ingredient_name'),
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user2, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [self.list_ing2])

        # Delete custom ingredient
        ing_list = [self.list_ing1, self.list_ing2, self.list_cust_ing2]

        UserListIngredients.objects.create(
            user=self.user2,
            list_name=self.list_name2,
            ingredients=ing_list
        )
        user_list = UserListIngredients.objects.get(user=self.user2, list_name=self.list_name2)
        self.assertEqual(len(user_list.ingredients), 3)

        delete_list_ingredient(
            username=self.user2.username,
            list_name=self.list_name2.list_name,
            ingredient=self.list_cust_ing2.get('ingredient_name'),
            unit=self.list_cust_ing2.get('unit'),
            is_custom_ingredient=self.list_cust_ing2.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user2, list_name=self.list_name2)
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [self.list_ing1, self.list_ing2])

        # Deleting in a non-existent list raises error
        with self.assertRaises(UserListIngredients.DoesNotExist):
            delete_list_ingredient(
                username=self.user2.username,
                list_name=self.empty_list_name1.list_name,
                ingredient=self.list_ing1.get('ingredient_name'),
                unit=self.list_ing1.get('unit'),
                is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
            )

    def test_add_list_ingredient(self):
        """
        Testing add_list_ingredient correctly adds an ingredient in a user's list
        """
        # Adding ingredient to an empty list
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 0)
        add_list_ingredient(
            username=self.user1.username,
            list_name=self.list_name1.list_name,
            ingredient=self.list_ing1.get('ingredient_name'),
            amount=self.list_ing1.get('amount'),
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [self.list_ing1])

        # Adding to same ingredient in a list
        add_list_ingredient(
            username=self.user1.username,
            list_name=self.list_name1.list_name,
            ingredient=self.list_ing1.get('ingredient_name'),
            amount=100,
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        updated_ing1 = {
            **self.list_ing1,
            'amount': self.list_ing1.get('amount') + 100
        }
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [updated_ing1])

        # Adding different ingredient to a list
        add_list_ingredient(
            username=self.user1.username,
            list_name=self.list_name1.list_name,
            ingredient=self.list_ing2.get('ingredient_name'),
            amount=self.list_ing2.get('amount'),
            unit=self.list_ing2.get('unit'),
            is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [updated_ing1, self.list_ing2])

        # Adding custom ingredient to a list
        add_list_ingredient(
            username=self.user1.username,
            list_name=self.list_name1.list_name,
            ingredient=self.list_cust_ing1.get('ingredient_name'),
            amount=self.list_cust_ing1.get('amount'),
            unit=self.list_cust_ing1.get('unit'),
            is_custom_ingredient=self.list_cust_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 3)
        self.assertEqual(user_list.ingredients, [updated_ing1, self.list_ing2, self.list_cust_ing1])

        # Adding a non-existent list raises error
        with self.assertRaises(UserListIngredients.DoesNotExist):
            add_list_ingredient(
                username=self.user1.username,
                list_name=self.empty_list_name1.list_name,
                ingredient=self.list_ing2.get('ingredient_name'),
                amount=self.list_ing2.get('amount'),
                unit=self.list_ing2.get('unit'),
                is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
            )

        # Adding a item with too high of an amount raises an error
        with self.assertRaises(ValueError):
            add_list_ingredient(
                username=self.user1.username,
                list_name=self.list_name1,
                ingredient=self.list_ing2.get('ingredient_name'),
                amount=15000,
                unit=self.list_ing2.get('unit'),
                is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
            )

    def test_set_list_ingredient(self):
        """
        Testing set_list_ingredient correctly updates an ingredient in a user's list
        """
        # Setting an ingredient in an empty list
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name1,
            ingredients=[]
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 0)
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=self.list_ing2.get('ingredient_name'),
            old_amount=0,
            old_unit=self.list_ing2.get('unit'),
            old_is_custom_ingredient=self.list_ing2.get('is_custom_ingredient'),
            new_list_name=self.list_name1.list_name,
            new_ingredient=self.list_ing1.get('ingredient_name'),
            new_amount=self.list_ing1.get('amount'),
            new_unit=self.list_ing1.get('unit'),
            new_is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [self.list_ing1])

        # Setting the same ingredient in the list
        updated_ing1 = {
            **self.list_ing1,
            'amount': 100,
            'unit': self.unit2.unit
        }
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=self.list_ing1.get('ingredient_name'),
            old_amount=self.list_ing1.get('amount'),
            old_unit=self.list_ing1.get('unit'),
            old_is_custom_ingredient=self.list_ing1.get('is_custom_ingredient'),
            new_list_name=self.list_name1.list_name,
            new_ingredient=updated_ing1.get('ingredient_name'),
            new_amount=updated_ing1.get('amount'),
            new_unit=updated_ing1.get('unit'),
            new_is_custom_ingredient=updated_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [updated_ing1])

        # Setting the same ingredient in the list with only some amount
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=updated_ing1.get('ingredient_name'),
            old_amount=updated_ing1.get('amount') / 2,
            old_unit=updated_ing1.get('unit'),
            old_is_custom_ingredient=updated_ing1.get('is_custom_ingredient'),
            new_list_name=self.list_name1.list_name,
            new_ingredient=updated_ing1.get('ingredient_name'),
            new_amount=updated_ing1.get('amount'),
            new_unit=updated_ing1.get('unit'),
            new_is_custom_ingredient=updated_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        updated_ing1 = {
            **updated_ing1,
            'amount': updated_ing1.get('amount') + updated_ing1.get('amount') / 2
        }
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [updated_ing1])

        # Setting the same ingredient in the list with only some amount
        # to a new unit
        updated_ing2 = {
            **self.list_ing1,
            'amount': 50
        }
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=updated_ing1.get('ingredient_name'),
            old_amount=updated_ing2.get('amount'),
            old_unit=updated_ing1.get('unit'),
            old_is_custom_ingredient=updated_ing1.get('is_custom_ingredient'),
            new_list_name=self.list_name1.list_name,
            new_ingredient=updated_ing2.get('ingredient_name'),
            new_amount=updated_ing2.get('amount'),
            new_unit=updated_ing2.get('unit'),
            new_is_custom_ingredient=updated_ing2.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        updated_ing1 = {
            **updated_ing1,
            'amount': updated_ing1.get('amount') - updated_ing2.get('amount')
        }
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [updated_ing1, updated_ing2])

        # Setting a different ingredient in a list when there are values in it
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=self.list_ing2.get('ingredient_name'),
            old_amount=0,
            old_unit=self.list_ing2.get('unit'),
            old_is_custom_ingredient=self.list_ing2.get('is_custom_ingredient'),
            new_list_name=self.list_name1.list_name,
            new_ingredient=self.list_ing2.get('ingredient_name'),
            new_amount=self.list_ing2.get('amount'),
            new_unit=self.list_ing2.get('unit'),
            new_is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 3)
        self.assertEqual(user_list.ingredients, [updated_ing1, updated_ing2, self.list_ing2])

        # Setting a non-existent list raises error
        with self.assertRaises(UserListIngredients.DoesNotExist):
            set_list_ingredient(
                username=self.user1.username,
                old_list_name=self.empty_list_name1.list_name,
                old_ingredient=self.list_ing2.get('ingredient_name'),
                old_amount=0,
                old_unit=self.list_ing2.get('unit'),
                old_is_custom_ingredient=self.list_ing2.get('is_custom_ingredient'),
                new_list_name=self.empty_list_name1.list_name,
                new_ingredient=self.list_ing2.get('ingredient_name'),
                new_amount=self.list_ing2.get('amount'),
                new_unit=self.list_ing2.get('unit'),
                new_is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
            )

        # Moving the ingredient entirely from one list to another
        UserListIngredients.objects.create(
            user=self.user1,
            list_name=self.list_name2,
            ingredients=[]
        )
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=updated_ing2.get('ingredient_name'),
            old_amount=updated_ing2.get('amount'),
            old_unit=updated_ing2.get('unit'),
            old_is_custom_ingredient=updated_ing2.get('is_custom_ingredient'),
            new_list_name=self.list_name2.list_name,
            new_ingredient=updated_ing2.get('ingredient_name'),
            new_amount=updated_ing2.get('amount'),
            new_unit=updated_ing2.get('unit'),
            new_is_custom_ingredient=updated_ing2.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [updated_ing1, self.list_ing2])

        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name2)
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [updated_ing2])

        # Moving the ingredient not in one list to another list
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=updated_ing2.get('ingredient_name'),
            old_amount=updated_ing2.get('amount'),
            old_unit=updated_ing2.get('unit'),
            old_is_custom_ingredient=updated_ing2.get('is_custom_ingredient'),
            new_list_name=self.list_name2.list_name,
            new_ingredient=updated_ing2.get('ingredient_name'),
            new_amount=updated_ing2.get('amount'),
            new_unit=updated_ing2.get('unit'),
            new_is_custom_ingredient=updated_ing2.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [updated_ing1, self.list_ing2])

        updated_ing2 = {
            **updated_ing2,
            'amount': updated_ing2.get('amount') * 2
        }

        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name2)
        self.assertEqual(len(user_list.ingredients), 1)
        self.assertEqual(user_list.ingredients, [updated_ing2])

        # Moving the ingredient partially from one list to another list
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=updated_ing1.get('ingredient_name'),
            old_amount=updated_ing1.get('amount') / 2,
            old_unit=updated_ing1.get('unit'),
            old_is_custom_ingredient=updated_ing1.get('is_custom_ingredient'),
            new_list_name=self.list_name2.list_name,
            new_ingredient=updated_ing1.get('ingredient_name'),
            new_amount=updated_ing1.get('amount') / 2,
            new_unit=updated_ing1.get('unit'),
            new_is_custom_ingredient=updated_ing1.get('is_custom_ingredient')
        )

        updated_ing1 = {
            **updated_ing1,
            'amount': updated_ing1.get('amount') / 2
        }

        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [updated_ing1, self.list_ing2])

        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name2)
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [updated_ing2, updated_ing1])

        # Setting a item with too high of an amount raises an error
        with self.assertRaises(ValueError):
            set_list_ingredient(
                username=self.user1.username,
                old_list_name=self.list_name1,
                old_ingredient=updated_ing1.get('ingredient_name'),
                old_amount=updated_ing1.get('amount') / 2,
                old_unit=updated_ing1.get('unit'),
                old_is_custom_ingredient=updated_ing1.get('is_custom_ingredient'),
                new_list_name=self.list_name1,
                new_ingredient=updated_ing1.get('ingredient_name'),
                new_amount=15000,
                new_unit=updated_ing1.get('unit'),
                new_is_custom_ingredient=updated_ing1.get('is_custom_ingredient')
            )

        # Setting a custom ingredient in a list
        set_list_ingredient(
            username=self.user1.username,
            old_list_name=self.list_name1.list_name,
            old_ingredient=self.list_ing2.get('ingredient_name'),
            old_amount=self.list_ing2.get('amount'),
            old_unit=self.list_ing2.get('unit'),
            old_is_custom_ingredient=self.list_ing2.get('is_custom_ingredient'),
            new_list_name=self.list_name1.list_name,
            new_ingredient=self.list_cust_ing1.get('ingredient_name'),
            new_amount=self.list_cust_ing1.get('amount'),
            new_unit=self.list_cust_ing1.get('unit'),
            new_is_custom_ingredient=self.list_cust_ing1.get('is_custom_ingredient')
        )
        user_list = UserListIngredients.objects.get(user=self.user1, list_name=self.list_name1)
        self.assertEqual(len(user_list.ingredients), 2)
        self.assertEqual(user_list.ingredients, [updated_ing1, self.list_cust_ing1])


class RecipeQueries(TestCase):
    user1 = None
    ing1 = None
    ing2 = None
    cust_ing1 = None
    recipe_name1 = None
    recipe_name2 = None
    empty_recipe_name = None
    unit1 = None
    unit2 = None
    list_ing1 = None
    list_ing2 = None
    list_cust_ing1 = None
    step1 = None
    step2 = None

    def setUp(self):
        self.user1 = User.objects.create(username='test_user1', email='user1@test.com')
        self.ing1 = Ingredient.objects.create(name='test_ingredient1', type='test_type1')
        self.ing2 = Ingredient.objects.create(name='test_ingredient2', type='test_type1')
        self.cust_ing1 = CustomIngredient.objects.create(
            user=self.user1,
            name=self.ing1.name,
            type=self.ing1.type
        )
        self.recipe_name1 = 'test_recipename1'
        self.recipe_name2 = 'test_recipename2'
        self.empty_recipe_name = 'empty_recipename1'
        self.unit1 = Measurement.objects.create(unit='test_unit1')
        self.unit2 = Measurement.objects.create(unit='test_unit2')
        self.list_ing1 = {
            'ingredient_name': self.ing1.name,
            'ingredient_type': self.ing1.type,
            'amount': 500,
            'unit': self.unit1.unit,
            'is_custom_ingredient': False
        }
        self.list_ing2 = {
            'ingredient_name': self.ing2.name,
            'ingredient_type': self.ing2.type,
            'amount': 400,
            'unit': self.unit2.unit,
            'is_custom_ingredient': False
        }
        self.list_cust_ing1 = {
            'ingredient_name': self.cust_ing1.name,
            'ingredient_type': self.cust_ing1.type,
            'amount': 500,
            'unit': self.unit1.unit,
            'is_custom_ingredient': True
        }
        self.step1 = "This is the first step in my recipe!"
        self.step2 = "This is the second step in my recipe!"

    def test_create_recipe(self):
        """
        Testing create_recipe creates a recipe in the database.
        """
        create_recipe(username=self.user1.username, recipe_name=self.recipe_name1)
        create_recipe(username=self.user1.username, recipe_name=self.recipe_name2)

        user_recipes = Recipe.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(user_recipes), 2)
        self.assertEqual(user_recipes[0].user, self.user1)
        self.assertEqual(user_recipes[0].recipe_name, self.recipe_name1)
        self.assertEqual(len(user_recipes[0].ingredients), 0)
        self.assertEqual(len(user_recipes[0].steps), 0)

        self.assertEqual(user_recipes[1].user, self.user1)
        self.assertEqual(user_recipes[1].recipe_name, self.recipe_name2)
        self.assertEqual(len(user_recipes[1].ingredients), 0)
        self.assertEqual(len(user_recipes[1].steps), 0)

    def test_delete_recipe(self):
        """
        Testing delete_recipe deletes a recipe from the database.
        """
        Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name2,
            steps=[],
            ingredients=[]
        )

        recipes_list = Recipe.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(recipes_list), 2)
        self.assertEqual(recipes_list[0].user, self.user1)
        self.assertEqual(recipes_list[0].recipe_name, self.recipe_name1)
        self.assertEqual(len(recipes_list[0].ingredients), 0)
        self.assertEqual(len(recipes_list[0].steps), 0)

        self.assertEqual(recipes_list[1].user, self.user1)
        self.assertEqual(recipes_list[1].recipe_name, self.recipe_name2)
        self.assertEqual(len(recipes_list[1].ingredients), 0)
        self.assertEqual(len(recipes_list[1].steps), 0)

        delete_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1
        )
        delete_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2
        )
        recipes_list = Recipe.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(recipes_list), 0)

        delete_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1
        )
        recipes_list = UserListIngredients.objects.filter(user__username=self.user1.username)
        self.assertEqual(len(recipes_list), 0)

    def test_add_ingredient_to_recipe(self):
        """
        Testing add_ingredient_to_recipe correctly adds an ingredient to a user's recipe
        """
        # Adding ingredient to an empty recipe
        Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.ingredients), 0)
        add_ingredient_to_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            ingredient=self.list_ing1.get('ingredient_name'),
            amount=self.list_ing1.get('amount'),
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.ingredients), 1)
        self.assertEqual(user_recipe.ingredients, [self.list_ing1])

        # Adding to same ingredient in a recipe
        add_ingredient_to_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            ingredient=self.list_ing1.get('ingredient_name'),
            amount=100,
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        updated_ing1 = {
            **self.list_ing1,
            'amount': self.list_ing1.get('amount') + 100
        }
        self.assertEqual(len(user_recipe.ingredients), 1)
        self.assertEqual(user_recipe.ingredients, [updated_ing1])

        # Adding different ingredient to a recipe
        add_ingredient_to_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            ingredient=self.list_ing2.get('ingredient_name'),
            amount=self.list_ing2.get('amount'),
            unit=self.list_ing2.get('unit'),
            is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.ingredients), 2)
        self.assertEqual(user_recipe.ingredients, [updated_ing1, self.list_ing2])

        # Adding custom ingredient to a recipe
        add_ingredient_to_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            ingredient=self.list_cust_ing1.get('ingredient_name'),
            amount=self.list_cust_ing1.get('amount'),
            unit=self.list_cust_ing1.get('unit'),
            is_custom_ingredient=self.list_cust_ing1.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.ingredients), 3)
        self.assertEqual(
            user_recipe.ingredients,
            [updated_ing1, self.list_ing2, self.list_cust_ing1]
        )

        # Adding a non-existent recipe raises error
        with self.assertRaises(Recipe.DoesNotExist):
            add_ingredient_to_recipe(
                username=self.user1.username,
                recipe_name=self.empty_recipe_name,
                ingredient=self.list_ing2.get('ingredient_name'),
                amount=self.list_ing2.get('amount'),
                unit=self.list_ing2.get('unit'),
                is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
            )

        # Adding a item with too high of an amount raises an error
        with self.assertRaises(ValueError):
            add_ingredient_to_recipe(
                username=self.user1.username,
                recipe_name=self.recipe_name1,
                ingredient=self.list_ing2.get('ingredient_name'),
                amount=15000,
                unit=self.list_ing2.get('unit'),
                is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
            )

    def test_remove_ingredient_from_recipe(self):
        """
        Testing remove_ingredient_from_recipe correctly removes an ingredient from a user's recipe
        """
        user_recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        self.assertEqual(len(user_recipe.ingredients), 0)

        # Removing ingredient from an empty recipe
        remove_ingredient_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            ingredient=self.list_ing1.get('ingredient_name'),
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.ingredients), 0)

        user_recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name2,
            steps=[],
            ingredients=[self.list_ing1, self.list_cust_ing1]
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.ingredients), 2)

        # Removing ingredient not in the recipe
        remove_ingredient_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2,
            ingredient=self.list_ing2.get('ingredient_name'),
            unit=self.list_ing2.get('unit'),
            is_custom_ingredient=self.list_ing2.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.ingredients), 2)

        # Removing ingredient from a recipe
        remove_ingredient_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2,
            ingredient=self.list_ing1.get('ingredient_name'),
            unit=self.list_ing1.get('unit'),
            is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.ingredients), 1)

        # Removing custom ingredient from a recipe
        remove_ingredient_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2,
            ingredient=self.list_cust_ing1.get('ingredient_name'),
            unit=self.list_cust_ing1.get('unit'),
            is_custom_ingredient=self.list_cust_ing1.get('is_custom_ingredient')
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.ingredients), 0)

        # Removing ingredient from non-existant recipe raises error
        with self.assertRaises(Recipe.DoesNotExist):
            remove_ingredient_from_recipe(
                username=self.user1.username,
                recipe_name=self.empty_recipe_name,
                ingredient=self.list_ing1.get('ingredient_name'),
                unit=self.list_ing1.get('unit'),
                is_custom_ingredient=self.list_ing1.get('is_custom_ingredient')
            )

    def test_add_step_to_recipe(self):
        """
        Testing add_step_to_recipe correctly adds a step to a user's recipe
        """
        user_recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        self.assertEqual(len(user_recipe.steps), 0)

        # Adding step to an empty recipe
        add_step_to_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            step=self.step1
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.steps), 1)

        # Adding different step to a list
        add_step_to_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            step=self.step2
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.steps), 2)

        # Adding a non-existent recipe raises error
        with self.assertRaises(Recipe.DoesNotExist):
            add_step_to_recipe(
                username=self.user1.username,
                recipe_name=self.empty_recipe_name,
                step=self.step2
            )

    def test_remove_step_from_recipe(self):
        """
        Testing remove_step_from_recipe correctly removes a step in a user's recipe
        """
        user_recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        self.assertEqual(len(user_recipe.steps), 0)

        # Removing step 0 in an empty recipe. Steps start from 1
        remove_step_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            step_number=len(user_recipe.steps)
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.steps), 0)

        # Removing non existant step in an empty recipe.
        remove_step_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            step_number=len(user_recipe.steps) + 1
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.steps), 0)

        user_recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name2,
            steps=[self.step1],
            ingredients=[]
        )
        self.assertEqual(len(user_recipe.steps), 1)

        # Removing step not in recipe (index out of bounds)
        remove_step_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2,
            step_number=len(user_recipe.steps) + 1
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.steps), 1)

        # Removing step in recipe
        remove_step_from_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2,
            step_number=len(user_recipe.steps)
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.steps), 0)

        # Removing from a non-existent recipe raises error
        with self.assertRaises(Recipe.DoesNotExist):
            remove_step_from_recipe(
                username=self.user1.username,
                recipe_name=self.empty_recipe_name,
                step_number=len(user_recipe.steps)
            )

    def test_edit_step_in_recipe(self):
        """
        Testing edit_step_in_recipe correctly modifies a step in a user's recipe
        """
        user_recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        self.assertEqual(len(user_recipe.steps), 0)

        # Editing step 0 in an empty recipe. Steps start from 1
        edit_step_in_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            new_step=self.step1,
            step_number=0
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.steps), 0)

        # Editing non-existant step in an empty recipe.
        edit_step_in_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name1,
            new_step=self.step1,
            step_number=len(user_recipe.steps) + 1
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name1)
        self.assertEqual(len(user_recipe.steps), 0)

        user_recipe = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name2,
            steps=[self.step1],
            ingredients=[]
        )
        self.assertEqual(len(user_recipe.steps), 1)

        # Editing step not in recipe (index out of bounds)
        edit_step_in_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2,
            new_step=self.step2,
            step_number=len(user_recipe.steps) + 1
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.steps), 1)
        self.assertEqual(user_recipe.steps[0], self.step1)

        # Editing step in recipe
        edit_step_in_recipe(
            username=self.user1.username,
            recipe_name=self.recipe_name2,
            new_step=self.step2,
            step_number=len(user_recipe.steps)
        )
        user_recipe = Recipe.objects.get(user=self.user1, recipe_name=self.recipe_name2)
        self.assertEqual(len(user_recipe.steps), 1)
        self.assertEqual(user_recipe.steps[0], self.step2)

        # Editing step in a non-existent recipe raises error
        with self.assertRaises(Recipe.DoesNotExist):
            edit_step_in_recipe(
                username=self.user1.username,
                recipe_name=self.empty_recipe_name,
                new_step=self.step1,
                step_number=len(user_recipe.steps)
            )

    def test_get_all_recipes(self):
        """
        Testing get_all_recipes correctly gets all recipes given a user's name
        """
        all_recipes = get_all_recipes(self.user1.username)
        self.assertEqual(len(all_recipes), 0)

        Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        all_recipes = get_all_recipes(self.user1.username)
        self.assertEqual(len(all_recipes), 1)

        Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name2,
            steps=[],
            ingredients=[]
        )
        all_recipes = get_all_recipes(self.user1.username)
        self.assertEqual(len(all_recipes), 2)

    def test_get_recipe(self):
        """
        Testing get_recipe correctly gets a recipe given a user's name and recipe name
        """
        with self.assertRaises(Recipe.DoesNotExist):
            get_recipe(self.user1.username, self.recipe_name1)

        recipe_created = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name1,
            steps=[],
            ingredients=[]
        )
        recipe = get_recipe(self.user1.username, self.recipe_name1)
        self.assertEqual(recipe, recipe_created)

        recipe_created2 = Recipe.objects.create(
            user=self.user1,
            recipe_name=self.recipe_name2,
            steps=[],
            ingredients=[]
        )
        recipe = get_recipe(self.user1.username, self.recipe_name2)
        self.assertEqual(recipe, recipe_created2)
