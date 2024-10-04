from django.test import TestCase
from .models import Ingredient
from .queries import get_all_ingredients
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from django.core.management import call_command
from pymongo import MongoClient
# Create your tests here.
class TestIngredients(TestCase):
    def setUp(self):
        call_command('flush', verbosity=0, interactive=False)  # This ensures a clean state
        Ingredient.objects.create(name="testing",type="TEST")
        #new_ingredient = Ingredient("testing","TEST")
        #new_ingredient.save()
    def test_get_all_ingredients(self):
        #uri = "mongodb+srv://Vaughn:test@cluster0.8fysf.mongodb.net/CupboardDB?retryWrites=true&w=majority"
        #client = MongoClient(uri)
        #db = client.CupBoardDB
        #ingredients = db.ingredients.find()
        ingredients_list = get_all_ingredients()
        for item in ingredients_list:
            print(item)
        #for ingredient in ingredients:
        #    print(ingredient)
        