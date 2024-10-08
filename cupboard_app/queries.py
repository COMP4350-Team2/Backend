from django.db.models.query import QuerySet

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User
)

CREATE_SUCCESS_MSG = 'Item created successfully.'
UPDATE_SUCCESS_MSG = 'Item updated successfully.'
CREATE_FAILED_MSG = 'Failed to create item.'
UPDATE_FAILED_MSG = 'Failed to update item.'
EXISTS_MSG = 'Item already exists.'
DOES_NOT_EXIST_MSG = 'Item does not exist.'


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


def create_list(listName: str) -> str:
    """
    Creates a list in the list dimension table.

    Args:
        listName: List name

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = CREATE_SUCCESS_MSG
    try:
        if ListName.objects.filter(listName=listName).exists():
            result = EXISTS_MSG
        else:
            ListName.objects.get_or_create(listName=listName)
    except Exception:
        result = CREATE_FAILED_MSG

    return result


def get_all_lists() -> QuerySet:
    """
    Gets all the lists in the lists dimension table.

    Returns:
        QuerySet of all the lists.
    """
    return ListName.objects.all()


def get_list(listName: str, id: int = None) -> ListName | None:
    """
    Gets the specific list object from the database.

    Args:
        listName: List name
        id: List ID

    Returns:
        ListName object or None if ingredient is not found.
    """
    try:
        if id:
            result = ListName.objects.get(id=id)
        else:
            result = ListName.objects.get(listName=listName)
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
        {"ingredientId": id, "amount": amount, "unitId": id}
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
            "ingredientId": ingredient.id,
            "amount": amount,
            "unitId": unit.id
        }

    return ingredient_dict
