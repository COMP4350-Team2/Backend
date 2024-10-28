from django.db.models.query import QuerySet

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients
)

INVALID_USER_LIST = 'User list does not exist.'
DOES_NOT_EXIST = 'matching query does not exist.'
INVALID_ACTION = 'Action has to be either "ADD" or "DELETE"'
ADD_ACTION = 'ADD'
REMOVE_ACTION = 'REMOVE'


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
        Ingredient object or None if ingredient is not found.
    """
    try:
        if id:
            result = Ingredient.objects.get(id=id)
        else:
            result = Ingredient.objects.get(name=name)
    except Ingredient.DoesNotExist:
        result = None

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
        ListName object or None if ingredient is not found.
    """
    try:
        if id:
            result = ListName.objects.get(id=id)
        else:
            result = ListName.objects.get(list_name=list_name)
    except ListName.DoesNotExist:
        result = None

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
        Measurement object or None if measurement is not found.
    """
    try:
        if id:
            result = Measurement.objects.get(id=id)
        else:
            result = Measurement.objects.get(unit=unit)
    except Measurement.DoesNotExist:
        result = None

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
        User object or None if user is not found.
    """
    result = None
    if isinstance(username, str) and (isinstance(id, int) or id is None):
        try:
            if id:
                result = User.objects.get(id=id)
            else:
                result = User.objects.get(username=username)
        except User.DoesNotExist:
            result = None

    return result


def create_list_ingredient(ingredient: str, amount: int | float, unit: str) -> dict | None:
    """
    Creates the ingredient that will be in the user_list_ingredient

    Args:
        ingredient: Ingredient name
        amount: Ingredient quantity
        unit: unit of measure for the ingredient

    Returns:
        The ingredient dictionary in the form of:
        {
            "ingredient_id": id,
            "ingredient_name": name,
            "amount": amount,
            "unit_id": id,
            "unit": unit
        }
        Exception raised if the ingredient or unit does not exist in the database
        or amount is not int or float type
    """
    ingredient = Ingredient.objects.get(name=ingredient)
    unit = Measurement.objects.get(unit=unit)
    if isinstance(amount, int) or isinstance(amount, float):
        ingredient_dict = {
            'ingredient_id': ingredient.id,
            'ingredient_name': ingredient.name,
            'amount': amount,
            'unit_id': unit.id,
            'unit': unit.unit
        }
    else:
        raise ValueError('Amount must be of type int or float.')

    return ingredient_dict


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
            user__id=id
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

    return result


def update_list_ingredient(
    username: str,
    list_name: str,
    ingredient: str,
    amount: int | float,
    unit: str,
    action: str
) -> UserListIngredients:
    """
    Updates an ingredient in the user's list.

    If ingredient exists in the user's list and has the same unit,
    then update the given ingredient's amount.

    If ingredient exists in the user's list and has a different unit,
    then add new ingredient dictionary to user's list if action is ADD.

    If ingredient does not exist in the user's list, then add new ingredient
    dictionary to user's list if action is ADD.

    Args:
        username: User's username
        list_name: Name of the list
        ingredient: Name of the ingredient
        amount: Quantity of the ingredient
        unit: The unit of measure for the ingredient
        action: How to update the ingredient. Either ADD or DELETE

    Returns:
        The updated UserListIngredient object.
        Raises exception if update was unsuccessful
        or username, unit, or specified UserListIngredient does not exist
    """
    delete_ingredient = False
    list_ingredient = create_list_ingredient(
        ingredient=ingredient,
        amount=amount,
        unit=unit
    )
    # Check list exists
    user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=list_name
    ).first()
    if user_list:
        search_id = list_ingredient.get('ingredient_id')
        unit_id = list_ingredient.get('unit_id')
        # Check if ingredient exists
        if action == ADD_ACTION or action == REMOVE_ACTION:
            if action == ADD_ACTION and not user_list.ingredients:
                # Empty list so set the list
                user_list.ingredients = [list_ingredient]
            elif action == ADD_ACTION and not any(
                dictionary.get('ingredient_id', None) == search_id
                and dictionary.get('unit_id', None) == unit_id
                for dictionary in user_list.ingredients
            ):
                # ingredient does not exist so insert
                user_list.ingredients.append(list_ingredient)
            else:
                # ingredient exists so update ingredient
                for i in user_list.ingredients:
                    # if unit is the same just change amount
                    if i['ingredient_id'] == search_id and i['unit_id'] == unit_id:
                        if action == ADD_ACTION:
                            i['amount'] += amount
                        elif action == REMOVE_ACTION and i['amount'] > amount:
                            i['amount'] -= amount
                        elif action == REMOVE_ACTION and i['amount'] <= amount:
                            # Delete from list
                            delete_ingredient = True
        else:
            raise ValueError(INVALID_ACTION)

        if delete_ingredient:
            user_list = remove_list_ingredient(
                username=username,
                list_name=list_name,
                ingredient=ingredient,
                unit=unit
            )
        else:
            user_list.save()
    else:
        raise ValueError(INVALID_USER_LIST)

    return user_list


def create_user_list_ingredients(
    username: str,
    list_name: str,
    ingredients: list[dict] = []
) -> UserListIngredients:
    """
    Creates a user list in the UserListIngredients dimension table.

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

    obj, new_created = UserListIngredients.objects.get_or_create(
        user=user,
        list_name=list,
        ingredients=ingredients
    )

    return obj


def remove_list_ingredient(
    username: str,
    list_name: str,
    ingredient: str,
    unit: str
) -> UserListIngredients:
    """
    Removes an ingredient in the user's list.

    Args:
        username: User's username
        list_name: Name of the list
        ingredient: Ingredient name
        unit: The unit of measure for the ingredient

    Returns:
        The updated list.
    """
    user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=list_name
    ).first()
    if user_list and user_list.ingredients:
        # Check if ingredient exists, if so delete it
        for dictionary in user_list.ingredients:
            if (
                dictionary.get('ingredient_name', None) == ingredient
                and dictionary.get('unit', None) == unit
            ):
                user_list.ingredients.remove(dictionary)
        user_list.save()

    result = user_list

    return result


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
