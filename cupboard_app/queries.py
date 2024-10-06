from .models import Recipe
from .models import Ingredient
from .models import UserListIngredients
from .models import ListName
from .models import User
from .models import Measurement
import json

def get_listName_id(listName):
    listNameObject = ListName.objects.filter(listName=listName)
    return listNameObject.id

def get_user_id(username):
    userObject = User.objects.filter(username=username)
    return userObject.id

def get_measurement_id(unit):
    measurementObject = Measurement.objects.filter(unit=unit)
    return measurementObject.id

def get_ingredient_id(name):
    ingredientObject = Ingredient.objects.filter(name=name)
    return ingredientObject.id

def get_all_recipes():
    return Recipe.objects.all()

def get_all_ingredients():
    return Ingredient.objects.all()

# Given strings for username, list name, ingredient name, and unit
# Along with an integer value for amount 
# Add that ingredient to the list for the user with the associated amount
def insert_list_ingredient(username,listName,ingredient,amount,unit):
    list = UserListIngredients.objects.get(get_user_id(username),get_listName_id(listName))
    ingredient_dictionary = {"ingredientId":get_ingredient_id(ingredient),"amount":amount,"unitId":get_measurement_id(unit)}
    list.ingredients.append(ingredient_dictionary)

# Given strings for username, list name, ingredient name, and unit
# Along with an integer value for amount 
# Update the given ingredient's amount and unit to the passed amount and unit
def update_list_ingredient(username,listName,ingredient,amount,unit):
    list = UserListIngredients.objects.get(get_user_id(username),get_listName_id(listName))
    searchId = get_ingredient_id(ingredient)
    for i in list.ingredients:
        if(i["_id"] == searchId):
           i["amount"] = amount
           i["unitId"] = get_measurement_id(unit)