from django.db.models.query import QuerySet

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients,
    CustomIngredient
)

MAX_LISTS = 10
GROCERY_LIST_NAME = 'Grocery'
PANTRY_LIST_NAME = 'Pantry'
INVALID_USER_LIST = 'User list does not exist.'
DOES_NOT_EXIST = 'matching query does not exist.'
MAX_LISTS_PER_USER = f'User has {MAX_LISTS} lists. Max limit per user reached.'


def create_ingredient(name: str, type: str) -> Ingredient:
    """
    Creates an ingredient in the ingredient dimension table.

    Args:
        name: Ingredient name
        type: Ingredient type

    Returns:
        Ingredient object if new ingredient created or
        ingredient already existed in the database.
    """
    obj, new_created = Ingredient.objects.get_or_create(name=name, type=type)
    return obj


def get_all_ingredients() -> QuerySet:
    """
    Gets all the ingredients in the ingredients dimension table.

    Returns:
        QuerySet of all the ingredients.
    """
    return Ingredient.objects.all()


def get_ingredient(name: str, id: int = None) -> Ingredient | None:
    """
    Gets the specific ingredient object from the database.

    Args:
        name: Ingredient name
        id: Ingredient ID

    Returns:
        Ingredient object or exception if ingredient is not found.
    """
    if id:
        result = Ingredient.objects.get(id=id, name=name)
    else:
        result = Ingredient.objects.get(name=name)

    return result


def create_custom_ingredient(username: str, name: str, type: str) -> CustomIngredient:
    """
    Creates a custom ingredient in the custom ingredient dimension table.

    Args:
        username: User's username
        name: Ingredient name
        type: Ingredient type

    Returns:
        CustomIngredient object if new custom ingredient created or
        custom ingredient already existed for the user.
    """
    user = User.objects.get(username=username)
    obj, new_created = CustomIngredient.objects.get_or_create(user=user, name=name, type=type)
    return obj


def delete_custom_ingredient(username: str, ingredient: str):
    """
    Deletes a custom ingredient in the CustomIngredient dimension table.

    Args:
        username: User's username
        ingredient: Ingredient name.

    Returns:
        QuerySet of all the user's remaining custom ingredients.
    """
    user = User.objects.get(username=username)
    query = CustomIngredient.objects.all().filter(
        user=user,
        name=ingredient
    )

    if query.exists():
        query.get().delete()

    return get_all_custom_ingredients(username)


def get_all_custom_ingredients(username: str) -> QuerySet:
    """
    Gets all the custom ingredients in the custom ingredients dimension table.

    Returns:
        QuerySet of all the custom ingredients.
    """

    user = User.objects.get(username=username)
    return CustomIngredient.objects.all().filter(user=user)


def get_custom_ingredient(username: str, name: str, id: int = None) -> CustomIngredient | None:
    """
    Gets the specific custom ingredient object from the user.

    Args:
        username: User's username
        name: Ingredient name
        id: Ingredient ID

    Returns:
        CustomIngredient object or exception if ingredient is not found.
    """

    user = User.objects.get(username=username)
    if id:
        result = CustomIngredient.objects.get(user=user, id=id, name=name)
    else:
        result = CustomIngredient.objects.get(user=user, name=name)

    return result


def create_list_name(list_name: str) -> ListName:
    """
    Creates a list name in the listName dimension table.

    Args:
        list_name: List name

    Returns:
        ListName object if new list name created successfully or
        list name already existed in the database.
    """
    obj, new_created = ListName.objects.get_or_create(list_name=list_name)
    return obj


def get_all_list_names() -> QuerySet:
    """
    Gets all the list names in the database.

    Returns:
        QuerySet of all the lists.
    """
    return ListName.objects.all()


def get_list_name(list_name: str, id: int = None) -> ListName | None:
    """
    Gets the specific list name object from the database.

    Args:
        list_name: List name
        id: ListName ID

    Returns:
        ListName object or exception if ingredient is not found.
    """
    if id:
        result = ListName.objects.get(id=id, list_name=list_name)
    else:
        result = ListName.objects.get(list_name=list_name)

    return result


def create_measurement(unit: str) -> Measurement:
    """
    Creates a measurement unit in the measurement dimension table.

    Args:
        unit: The unit to add

    Returns:
        Measurement object if new measurement created successfully or
        measurement already existed in the database.
    """
    obj, new_created = Measurement.objects.get_or_create(unit=unit)
    return obj


def get_all_measurements() -> QuerySet:
    """
    Gets all the measurements in the measurements dimension table.

    Returns:
        QuerySet of all the measurements.
    """
    return Measurement.objects.all()


def get_measurement(unit: str, id: int = None) -> Measurement | None:
    """
    Gets the specific measurement object from the database.

    Args:
        unit: Measurement unit
        id: Measurement ID

    Returns:
        Measurement object or exception if measurement not found
    """
    if id:
        result = Measurement.objects.get(id=id, unit=unit)
    else:
        result = Measurement.objects.get(unit=unit)

    return result


def create_user(username: str, email: str) -> User:
    """
    Creates a user in the user dimension table.

    Args:
        username: User's username
        email: User's email address

    Returns:
        User object if new user created successfully or
        user already existed in the database.
    """
    obj, new_created = User.objects.get_or_create(username=username, email=email)
    return obj


def get_all_users() -> QuerySet:
    """
    Gets all the users in the users dimension table.

    Returns:
        QuerySet of all the users.
    """
    return User.objects.all()


def get_user(username: str, id: int = None) -> User | None:
    """
    Gets the specific user object from the database.

    Args:
        username: User's username
        id: User ID

    Returns:
        User object or exception if user not found.
    """
    result = None
    if isinstance(username, str) and (isinstance(id, int) or id is None):
        if id:
            result = User.objects.get(id=id, username=username)
        else:
            result = User.objects.get(username=username)

    return result


def create_list_ingredient(
    ingredient: str,
    amount: int | float,
    unit: str,
    user_id: int = None
) -> dict:
    """
    Creates the ingredient that will be in the user_list_ingredient

    Args:
        ingredient: Ingredient name
        amount: Ingredient quantity
        unit: unit of measure for the ingredient
        user_id: User ID

    Returns:
        The ingredient dictionary in the form of:
        {
            "ingredient_name": name,
            'ingredient_type': type,
            "amount": amount,
            "unit": unit,
            "is_custom_ingredient": bool if custom ingredient or not
        }
        Exception raised if the ingredient or unit does not exist in the database
        or amount is not int or float type
    """
    if user_id:
        ingredient_object = CustomIngredient.objects.get(name=ingredient, user__id=user_id)
        is_custom_ingredient = True
    else:
        ingredient_object = Ingredient.objects.get(name=ingredient)
        is_custom_ingredient = False

    unit = Measurement.objects.get(unit=unit)

    if isinstance(amount, int) or isinstance(amount, float):
        if (amount < 10000):
            ingredient_dict = {
                'ingredient_name': ingredient_object.name,
                'ingredient_type': ingredient_object.type,
                'amount': amount,
                'unit': unit.unit,
                'is_custom_ingredient': is_custom_ingredient
            }
        else:
            raise ValueError('Amount must be less than 10,000.')
    else:
        raise ValueError('Amount must be of type int or float.')

    return ingredient_dict


def delete_list_ingredient(
    username: str,
    list_name: str,
    ingredient: str,
    unit: str,
    is_custom_ingredient: bool
) -> UserListIngredients:
    """
    Deletes an ingredient in the user's list.

    Args:
        username: User's username
        list_name: Name of the list to update
        ingredient: Ingredient name
        unit: The unit of measure for the ingredient
        is_custom_ingredient: Whether the ingredient is custom or not

    Returns:
        The updated list.
    """
    if isinstance(is_custom_ingredient, str):
        is_custom_ingredient = is_custom_ingredient == 'True'

    user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=list_name
    ).first()

    if user_list:
        if user_list.ingredients:
            # Check if ingredient exists, if so delete it
            for dictionary in user_list.ingredients:
                if (
                    dictionary.get('ingredient_name', None) == ingredient
                    and dictionary.get('unit', None) == unit
                    and dictionary.get('is_custom_ingredient', None) == is_custom_ingredient
                ):
                    user_list.ingredients.remove(dictionary)
            user_list.save()
    else:
        raise ValueError(INVALID_USER_LIST)

    return user_list


def add_list_ingredient(
    username: str,
    list_name: str,
    ingredient: str,
    amount: int | float,
    unit: str,
    is_custom_ingredient: bool
) -> UserListIngredients:
    """
    Adds an ingredient in the user's list.

    If the ingredient already existed and then adds the specified
    amount to the ingredient's current amount instead.

    Args:
        username: User's username
        list_name: Name of the list to update
        ingredient: Ingredient name
        amount: Quantity of the ingredient
        unit: The unit of measure for the ingredient
        is_custom_ingredient: Whether the ingredient we are adding is custom

    Returns:
        The updated list.
    """
    if isinstance(is_custom_ingredient, str):
        is_custom_ingredient = is_custom_ingredient == 'True'

    user_id = None
    if is_custom_ingredient:
        user_id = User.objects.get(username=username).id

    # Create the ingredient to put into list
    list_ingredient = create_list_ingredient(
        ingredient=ingredient,
        amount=amount,
        unit=unit,
        user_id=user_id
    )

    user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=list_name
    ).first()

    if user_list:
        if not user_list.ingredients:
            # Empty list so set the list
            user_list.ingredients = [list_ingredient]
        elif not any(
            dictionary.get('ingredient_name', None) == ingredient
            and dictionary.get('unit', None) == unit
            and dictionary.get('is_custom_ingredient') == is_custom_ingredient
            for dictionary in user_list.ingredients
        ):
            # ingredient does not exist so insert
            user_list.ingredients.append(list_ingredient)
        else:
            # ingredient exists so add or set the ingredient
            for i in user_list.ingredients:
                if (
                    i['ingredient_name'] == ingredient
                    and i['unit'] == unit
                    and i['is_custom_ingredient'] == is_custom_ingredient
                ):
                    i['amount'] += amount
        user_list.save()
    else:
        raise ValueError(INVALID_USER_LIST)

    return user_list


def set_list_ingredient(
    username: str,
    old_list_name: str,
    old_ingredient: str,
    old_amount: int | float,
    old_unit: str,
    old_is_custom_ingredient: bool,
    new_list_name: str,
    new_ingredient: str,
    new_amount: int | float,
    new_unit: str,
    new_is_custom_ingredient: bool
) -> QuerySet:
    """
    Sets an ingredient's unit and amount in the user's list.

    If the new ingredient is not in the user's list, then
    adds the new ingredient to the user's list.

    Args:
        username: User's username
        old_list_name: Name of the list to delete from
        old_ingredient: Name of the ingredient to update
        old_amount: Quantity of the ingredient to remove
        old_unit: The unit of measure for the ingredient to update
        old_is_custom_ingredient: The custom ingredient flag of the ingredient to update
        new_list_name: Name of the list to update
        new_ingredient: Name of the ingredient to change to
        new_amount: Quantity of the ingredient to change to
        new_unit: The unit of measure for the ingredient to change to
        new_is_custom_ingredient: The custom ingredient flag of the ingredient to change to

    Returns:
        All of the user's updated lists.
    """
    if isinstance(old_is_custom_ingredient, str):
        old_is_custom_ingredient = old_is_custom_ingredient == 'True'

    if isinstance(new_is_custom_ingredient, str):
        new_is_custom_ingredient = new_is_custom_ingredient == 'True'

    user_id = None
    if new_is_custom_ingredient:
        user_id = User.objects.get(username=username).id

    # Create the ingredient to put into list
    list_ingredient = create_list_ingredient(
        ingredient=new_ingredient,
        amount=new_amount,
        unit=new_unit,
        user_id=user_id
    )

    # Get the list to set/remove ingredient from
    old_user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=old_list_name
    ).first()

    # Get the list to set/move ingredient to
    new_user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=new_list_name
    ).first()

    if not old_user_list or not new_user_list:
        raise ValueError(INVALID_USER_LIST)

    # Update the old list
    if old_user_list.ingredients:
        for ingredient in old_user_list.ingredients:
            if (
                ingredient['ingredient_name'] == old_ingredient
                and ingredient['unit'] == old_unit
                and ingredient['is_custom_ingredient'] == old_is_custom_ingredient
            ):
                if ingredient['amount'] <= old_amount:
                    old_user_list.ingredients.remove(ingredient)
                else:
                    ingredient['amount'] -= old_amount

    if old_list_name == new_list_name:
        # Same list so update the old_user_list
        new_user_list = old_user_list
        old_user_list = None
    else:
        # Different list so save the old_user_list
        # and continue with the new_user_list
        old_user_list.save()

    # Update the new list
    if not new_user_list.ingredients:
        # Empty list so set the list
        new_user_list.ingredients = [list_ingredient]
    elif not any(
        ingredient['ingredient_name'] == new_ingredient
        and ingredient['unit'] == new_unit
        and ingredient['is_custom_ingredient'] == new_is_custom_ingredient
        for ingredient in new_user_list.ingredients
    ):
        # ingredient does not exist so insert
        new_user_list.ingredients.append(list_ingredient)
    else:
        # ingredient exists so add or set the ingredient
        for ingredient in new_user_list.ingredients:
            if (
                ingredient['ingredient_name'] == new_ingredient
                and ingredient['unit'] == new_unit
                and ingredient['is_custom_ingredient'] == new_is_custom_ingredient
            ):
                ingredient['amount'] += new_amount

    new_user_list.save()

    return get_user_lists_ingredients(username=username)


def create_user_list_ingredients(
    username: str,
    list_name: str,
    ingredients: list[dict] = []
) -> UserListIngredients:
    """
    Creates a user list in the UserListIngredients dimension table. Users are limited
    to 10 lists.

    Args:
        username: User's username
        list_name: List name.
        ingredient: The array of dictionaries with ingredient information to add.

    Returns:
        UserListIngredients object if new UserListIngredients created successfully or
        UserListIngredients already existed in the database.
        Raises exception if the user or listName does not exist or problems with
        creating a new UserListIngredients object
    """
    user = User.objects.get(username=username)
    list = ListName.objects.get(list_name=list_name)

    query = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=list_name
    )

    if len(UserListIngredients.objects.filter(user__username=username)) < MAX_LISTS:
        if not query.exists():
            obj = UserListIngredients.objects.create(
                user=user,
                list_name=list,
                ingredients=ingredients
            )
        else:
            obj = query.first()
    else:
        raise ValueError(MAX_LISTS_PER_USER)

    return obj


def delete_user_list_ingredients(
    username: str,
    list_name: str
) -> QuerySet:
    """
    Deletes a user list in the UserListIngredients dimension table.

    Args:
        username: User's username
        list_name: List name.
        ingredient: The array of dictionaries with ingredient information to add.

    Returns:
        QuerySet of all the lists for the specific user after deletion.
    """
    query = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=list_name
    )
    if query.exists():
        query.get().delete()

    return get_user_lists_ingredients(username=username)


def get_user_lists_ingredients(username: str, id: int = None) -> QuerySet:
    """
    Gets all lists for the specific user from the database.

    Args:
        username: User's username
        id: User ID

    Returns:
        QuerySet of all the lists for the specific user.
    """
    if id:
        result = UserListIngredients.objects.filter(
            user__id=id,
            user__username=username
        )
    else:
        result = UserListIngredients.objects.filter(
            user__username=username
        )

    return result


def get_specific_user_lists_ingredients(
    username: str,
    list_name: str,
    id: int = None
) -> QuerySet:
    """
    Gets specific list for the specific user from the database.

    Args:
        username: User's username
        id: User ID
        list_name: Name of the list

    Returns:
        QuerySet of all the lists for the specific user.
    """
    if id:
        result = UserListIngredients.objects.filter(
            user__id=id,
            list_name__list_name=list_name
        ).first()
    else:
        result = UserListIngredients.objects.filter(
            user__username=username,
            list_name__list_name=list_name
        ).first()

    if not result:
        raise ValueError(INVALID_USER_LIST)

    return result


def change_user_list_ingredient_name(
    username: str,
    old_list_name: str,
    new_list_name: str
) -> UserListIngredients:
    """
    Changes a user's list name to another list name.

    Args:
        username: User's username
        old_list_name: Name of the list to update
        new_list_name: Name of the list to change to

    Returns:
        The updated UserListIngredient object.
        Raises exception if update was unsuccessful.
    """
    user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=old_list_name
    ).first()

    if user_list:
        if old_list_name != new_list_name:
            # Create the listName object if it doesn't already exist
            create_list_name(list_name=new_list_name)
            new_user_list = create_user_list_ingredients(
                username=username,
                list_name=new_list_name,
                ingredients=user_list.ingredients
            )
            delete_user_list_ingredients(username=username, list_name=old_list_name)
            user_list = new_user_list
    else:
        raise ValueError(INVALID_USER_LIST)

    return user_list


def add_default_user_lists(username: str):
    """
    Adds Grocery and Pantry lists by default.

    Args:
        username: User's username
    """
    create_list_name(list_name=GROCERY_LIST_NAME)
    create_list_name(list_name=PANTRY_LIST_NAME)
    create_user_list_ingredients(username=username, list_name=GROCERY_LIST_NAME)
    create_user_list_ingredients(username=username, list_name=PANTRY_LIST_NAME)
