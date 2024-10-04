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
        Ingredient.objects.create(name="testing",type="TEST")

    def test_get_all_ingredients(self):
        ingredients_list = get_all_ingredients()
        for item in ingredients_list:
            print(item)
        
