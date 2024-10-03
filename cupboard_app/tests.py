from django.test import TestCase
from .models import Ingredient
from .queries import get_all_ingredients
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Create your tests here.
class MongoDBConnectionTest(TestCase):

    def test_connection(self):
        uri = "mongodb+srv://Vaughn:test@cluster0.8fysf.mongodb.net/CupboardDB?retryWrites=true&w=majority"
        client = MongoClient(uri)
        
        try:
            client.admin.command('ping')
            self.assertTrue(True)  # Connection successful
        except Exception as e:
            self.fail(f"Failed to connect to MongoDB: {e}")

    def test_database_creation(self):
        # Ensure that Django can create a test database
        # You may want to actually create and assert conditions on your database here
        pass  # Implement your test logic here if needed
class TestIngredients(TestCase):
    def setUp(self):
        Ingredient.objects.create(name="testing",type="none")
    def test_get_all_ingredients(self):
        ingredients = get_all_ingredients()
        print(ingredients)
