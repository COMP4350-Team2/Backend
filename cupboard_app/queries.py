from .models import Recipe
from .models import Ingredient
from .models import UserListIngredients
from .models import ListName
from .models import User
from .models import Measurement


def get_listName_id(listName):
    listNameObject = ListName.objects.get(listName=listName)
    if listNameObject.exists():
        return listNameObject.id
    else:
        return None


def get_user_id(username):
    userObject = User.objects.get(username=username)
    if userObject.exists():
        return userObject.id
    else:
        return None


def get_measurement_id(unit):
    measurementObject = Measurement.objects.get(unit=unit)
    if measurementObject.exists():
        return measurementObject.id
    else:
        return None


def get_ingredient_id(name):
    ingredientObject = Ingredient.objects.get(name=name)
    if ingredientObject.exists():
        return ingredientObject.id
    else:
        return None


def get_all_recipes():
    return Recipe.objects.all()


def get_all_ingredients():
    return Ingredient.objects.all()


def get_listName(id):
    listNameObject = ListName.objects.get(id=id)
    if listNameObject.exists():
        return listNameObject.first().listName
    else:
        return None


def create_user(username, email):
    userObject = User.objects.get(username=username)
    userObject2 = User.objects.get(email=email)
    if userObject.exists() or userObject2.exists():
        print("Account Generation Failed.")
    else:
        newUser = User(username=username, email=email)
        newUser.save()


# Given strings for username, list name, ingredient name, and unit
# Along with an integer value for amount
# Add that ingredient to the list for the user with the associated amount
def insert_list_ingredient(username, listName, ingredient, amount, unit):
    list = UserListIngredients.objects.get(get_user_id(username), get_listName_id(listName))
    ingredient_dictionary = {
        "ingredientId": get_ingredient_id(ingredient),
        "amount": amount,
        "unitId": get_measurement_id(unit)
    }
    list.ingredients.append(ingredient_dictionary)


def update_list_ingredient(
    username: str,
    listName: str,
    ingredient: str,
    amount: str,
    unit: str
):
    """
    Given strings for username, list name, ingredient name, and unit
    Along with an integer value for amount
    Update the given ingredient's amount and unit to the passed amount and unit

    Args:
        username: username
        listname: list name
        ingredient: name of ingredient we are updating
        amount: amount of ingredient
        unit: ingredient unit
    """
    list = UserListIngredients.objects.get(get_user_id(username), get_listName_id(listName))
    searchId = get_ingredient_id(ingredient)
    for i in list.ingredients:
        if i["_id"] == searchId:
            i["amount"] = amount
            i["unitId"] = get_measurement_id(unit)


def get_all_user_lists(username: str):
    """
    Gets all of the user's lists from the database

    Args:
        username: String for the username

    Returns:
        All the user's lists from the database as a 2D array in the following format:

        lists[0][0] = {"listName": Pantry}
        lists[0][1] = {"ingredientId": Id, "amount": Integer, "unitId": Id}
        lists[0][2] = {"ingredientId": Id, "amount": Integer, "unitId": Id}
        ...
        lists[1][0] = {"listName":Grocery}
        lists[1][1] = {"ingredientId": Id, "amount": Integer, "unitId": Id}
        lists[1][2] = {"ingredientId": Id, "amount": Integer, "unitId": Id}
        ...
    """
    allLists = UserListIngredients.objects.filter(get_user_id(username))
    counter = 0
    lists = []
    for i in allLists:
        lists[counter] = []
        lists[counter].append({"listName": get_listName(i.listNameId)})
        for k in i.ingredients:
            lists[counter].append(
                {
                    "ingredientId": k["_id"],
                    "amount": k["amount"],
                    "unitId": k["unitId"]
                }
            )
        counter += 1
    return lists
