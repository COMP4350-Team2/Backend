from django.db.models.query import QuerySet

from .models import Ingredient
from .models import ListName
from .models import Measurement
from .models import User
from .models import UserListIngredients
from .models import Recipe

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
        Ingredient.objects.get_or_create(name=name, type=type)
    except Exception:
        result = CREATE_FAILED_MSG
        if Ingredient.objects.filter(name=name).exists():
            result = EXISTS_MSG

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
        ListName.objects.get_or_create(listName=listName)
    except Exception:
        result = CREATE_FAILED_MSG
        if ListName.objects.filter(listName=listName).exists():
            result = EXISTS_MSG

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
        Measurement.objects.get_or_create(unit=unit)
    except Exception:
        result = CREATE_FAILED_MSG
        if Measurement.objects.filter(unit=unit).exists():
            result = EXISTS_MSG

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
        User.objects.get_or_create(username=username, email=email)
    except Exception:
        result = CREATE_FAILED_MSG
        if User.objects.filter(username=username).exists():
            result = EXISTS_MSG

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
    if ingredient is not None and unit is not None:
        ingredient_dict = {
            "ingredientId": ingredient.id,
            "amount": amount,
            "unitId": unit.id
        }

    return ingredient_dict


def create_user_list_ingredients(
    username: str,
    listName: str,
    ingredients: list[dict] = []
) -> str:
    """
    Creates a user list in the UserListIngredients dimension table.

    Args:
        username: User's username
        listName: List name.
        ingredient: The array of dictionaries with ingredient information to add.

    Returns:
        Success message if the save was successful.
        Fail message or exists message if save was unsuccessful.
    """
    result = CREATE_SUCCESS_MSG
    try:
        user = get_user(username=username)
        list = get_list(listName=listName)
        if user is not None and list is not None:
            # Check if list exists
            if UserListIngredients.objects.filter(
                user__username=username,
                listName__listName=listName
            ).exists():
                result = EXISTS_MSG
            else:
                UserListIngredients.objects.create(
                    user=user,
                    listName=list,
                    ingredients=ingredients
                )
        else:
            result = CREATE_FAILED_MSG
    except Exception:
        result = CREATE_FAILED_MSG

    return result


def get_all_user_list_ingredients() -> QuerySet:
    """
    Gets all the users' lists in the UserListIngredients dimension table.

    Returns:
        QuerySet of all the users' lists.
    """
    return UserListIngredients.objects.all()


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


def get_user_specific_list_ingredients(
    username: str,
    listName: str,
    user_id: int = None,
    list_id: int = None
) -> UserListIngredients | None:
    """
    Gets all lists for the specific user from the database.

    Args:
        username: User's username
        listName: List name
        user_id: User ID
        list_id: List ID

    Returns:
        UserListIngredients object or None if UserListIngredients object is not found.
    """
    if username and listName:
        result = UserListIngredients.objects.filter(
            user__username=username,
            listName__listName=listName
        ).first()
    elif username and list_id:
        result = UserListIngredients.objects.filter(
            user__username=username,
            listName__id=list_id
        ).first()
    elif user_id and listName:
        result = UserListIngredients.objects.filter(
            user__id=user_id,
            listName__listName=listName
        ).first()
    else:
        result = UserListIngredients.objects.filter(
            user__id=user_id,
            listName__id=list_id
        ).first()

    return result


def update_list_ingredient(
    username: str,
    listName: str,
    ingredient: str,
    amount: int | float,
    unit: str
) -> str:
    """
    Updates an ingredient in the user's list.

    If ingredient exists in the user's list, then update the given ingredient's
    amount and unit in the passed amount and unit.

    If ingredient does not exist in the user's list, then add new ingredient
    dictionary to user's list.

    Args:
        username: User's username
        listName: Name of the list
        ingredient: Name of the ingredient
        amount: Quantity of the ingredient
        unit: The unit of measure for the ingredient
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
                listName__listName=listName
            ).first()
            if user_list:
                search_id = list_ingredient.get('ingredientId')
                unit_id = list_ingredient.get('unitId')
                # Check if ingredient exists
                if not any(
                    dictionary.get('ingredientId', None) == search_id
                    for dictionary in user_list.ingredients
                ):
                    # ingredient does not exist so insert
                    user_list.ingredients.append(list_ingredient)
                else:
                    # ingredient exists so update ingredient
                    for i in user_list.ingredients:
                        if i['ingredientId'] == search_id:
                            i['amount'] = amount
                            i['unitId'] = unit_id
                user_list.save()
                result = UPDATE_SUCCESS_MSG
            else:
                result = DOES_NOT_EXIST_MSG
        else:
            result = f'{UPDATE_FAILED_MSG} Ingredient does not exist.'
    except Exception:
        result = UPDATE_FAILED_MSG

    return result


def get_all_user_lists_pretty(username: str):
    """
    Gets all of the user's lists from the database in a pretty format.
    Ingredients and unit are in readable format, not ID.

    Args:
        username: User's username

    Returns:
        All the user's lists from the database as a 2D array in the following format:

        lists[0][0] = {"listName": Pantry}
        lists[0][1] = {"ingredient": name, "amount": Integer | Float, "unit": unit}
        lists[0][2] = {"ingredient": name, "amount": Integer | Float, "unit": unit}
        ...
        lists[1][0] = {"listName": Grocery}
        lists[1][1] = {"ingredient": name, "amount": Integer | Float, "unit": unit}
        lists[1][2] = {"ingredient": name, "amount": Integer | Float, "unit": unit}
        ...
    """
    all_lists = get_user_lists_ingredients(username=username)
    lists = []
    for list in all_lists:
        list_ingredients = []
        list_ingredients.append({'listName': list.listName.listName})
        for ingredient in list.ingredients:
            ingredient_obj = get_ingredient(name='', id=ingredient['ingredientId'])
            measurement_obj = get_measurement(unit='', id=ingredient['unitId'])
            list_ingredients.append(
                {
                    'ingredient': ingredient_obj.name,
                    'amount': ingredient['amount'],
                    'unit': measurement_obj.unit
                }
            )
        lists.append(list_ingredients)
    return lists


def get_all_recipes() -> QuerySet:
    """
    Gets all the recipes in the recipes dimension table.

    Returns:
        QuerySet of all the recipes.
    """
    return Recipe.objects.all()
