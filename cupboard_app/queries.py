from django.db.models.query import QuerySet

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients
)

CREATE_SUCCESS_MSG = 'Item created successfully.'
UPDATE_SUCCESS_MSG = 'Item updated successfully.'
CREATE_FAILED_MSG = 'Failed to create item.'
UPDATE_FAILED_MSG = 'Failed to update item.'
EXISTS_MSG = 'Item already exists.'
DOES_NOT_EXIST_MSG = 'Item does not exist.'
HAS_NO_ING_MSG = 'List has no ingredients.'


def create_ingredient(name: str, type: str) -> str:
    """
    Creates an ingredient in the ingredient dimension table.

    Args:
        name: Ingredient name
        type: Ingredient type

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = CREATE_SUCCESS_MSG
    try:
        if Ingredient.objects.filter(name=name).exists():
            result = EXISTS_MSG
        else:
            Ingredient.objects.get_or_create(name=name, type=type)
    except Exception:
        result = CREATE_FAILED_MSG

    return result


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


def create_list_name(list_name: str) -> str:
    """
    Creates a list name in the database.

    Args:
        list_name: List name

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = CREATE_SUCCESS_MSG
    try:
        if ListName.objects.filter(list_name=list_name).exists():
            result = EXISTS_MSG
        else:
            ListName.objects.get_or_create(list_name=list_name)
    except Exception:
        result = CREATE_FAILED_MSG

    return result


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


def create_measurement(unit: str) -> str:
    """
    Creates a measurement unit in the measurement dimension table.

    Args:
        unit: The unit to add

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = CREATE_SUCCESS_MSG
    try:
        if Measurement.objects.filter(unit=unit).exists():
            result = EXISTS_MSG
        else:
            Measurement.objects.get_or_create(unit=unit)
    except Exception:
        result = CREATE_FAILED_MSG

    return result


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


def create_user(username: str, email: str) -> str:
    """
    Creates a user in the user dimension table.

    Args:
        username: User's username
        email: User's email address

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = CREATE_SUCCESS_MSG
    try:
        if User.objects.filter(username=username).exists():
            result = EXISTS_MSG
        else:
            User.objects.get_or_create(username=username, email=email)
    except Exception:
        result = CREATE_FAILED_MSG

    return result


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
        {"ingredient_id": id, "amount": amount, "unit_id": id}
    """
    ingredient_dict = None
    ingredient = get_ingredient(name=ingredient)
    unit = get_measurement(unit=unit)
    if (
        ingredient is not None
        and unit is not None
        and (isinstance(amount, int) or isinstance(amount, float))
    ):
        ingredient_dict = {
            "ingredient_id": ingredient.id,
            "amount": amount,
            "unit_id": unit.id
        }

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


def update_list_ingredient(
    username: str,
    list_name: str,
    ingredient: str,
    amount: int | float,
    unit: str
) -> str:
    """
    Updates an ingredient in the user's list.

    If ingredient exists in the user's list and has the same unit,
    then update the given ingredient's amount and unit in the passed amount and unit.

    If ingredient exists in the user's list and has a different unit,
    then add new ingredient dictionary to user's list.

    If ingredient does not exist in the user's list, then add new ingredient
    dictionary to user's list.

    Args:
        username: User's username
        list_name: Name of the list
        ingredient: Name of the ingredient
        amount: Quantity of the ingredient
        unit: The unit of measure for the ingredient

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = UPDATE_FAILED_MSG
    try:
        list_ingredient = create_list_ingredient(
            ingredient=ingredient,
            amount=amount,
            unit=unit
        )
        if list_ingredient:
            # Check list exists
            user_list = UserListIngredients.objects.filter(
                user__username=username,
                list_name__list_name=list_name
            ).first()
            if user_list:
                search_id = list_ingredient.get('ingredient_id')
                unit_id = list_ingredient.get('unit_id')
                # Check if ingredient exists
                if not user_list.ingredients:
                    user_list.ingredients = [list_ingredient]
                elif not any(
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
                            i['amount'] = amount
                user_list.save()
                result = UPDATE_SUCCESS_MSG
            else:
                result = DOES_NOT_EXIST_MSG
        else:
            result = f'{UPDATE_FAILED_MSG} Ingredient does not exist.'
    except Exception:
        result = UPDATE_FAILED_MSG

    return result


def create_user_list_ingredients(
    username: str,
    list_name: str,
    ingredients: list[dict] = []
) -> str:
    """
    Creates a user list in the UserListIngredients dimension table.

    Args:
        username: User's username
        list_name: List name.
        ingredient: The array of dictionaries with ingredient information to add.

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = CREATE_SUCCESS_MSG
    try:
        user = get_user(username=username)
        list = get_list_name(list_name=list_name)
        if user is not None and list is not None:
            # Check if list exists
            if UserListIngredients.objects.filter(
                user__username=username,
                list_name__list_name=list_name
            ).exists():
                result = EXISTS_MSG
            else:
                UserListIngredients.objects.create(
                    user=user,
                    list_name=list,
                    ingredients=ingredients
                )
        else:
            result = CREATE_FAILED_MSG
    except Exception:
        result = CREATE_FAILED_MSG

    return result


def remove_list_ingredient(
    username: str,
    list_name: str,
    ingredient_id: str
) -> str:
    """
    Removes an ingredient in the user's list.

    Args:
        username: User's username
        list_name: Name of the list
        ingredient_id: Id of the ingredient

    Returns:
        Success message if the save was successful.
        Fail message, exists or empty list message if save was unsuccessful.
    """
    result = UPDATE_FAILED_MSG

    # Check list exists
    user_list = UserListIngredients.objects.filter(
        user__username=username,
        list_name__list_name=list_name
    ).first()
    if user_list and user_list.ingredients:
        # Check if ingredient exists, if so delete it
        for dictionary in user_list.ingredients:
            if dictionary.get('ingredient_id', None) == ingredient_id:
                user_list.ingredients.remove(dictionary)
        user_list.save()
        result = UPDATE_SUCCESS_MSG
    else:
        result = DOES_NOT_EXIST_MSG

    return result
