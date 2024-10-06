from django.test import TestCase
from .models import Ingredient
from .queries import get_all_ingredients
import json

# Create your tests here.
class TestIngredients(TestCase):
    def setUp(self):
        Ingredient.objects.create(name="testing", type="TEST")
        Ingredient.objects.create(name="testing2", type="TEST2")
    def test_get_all_ingredients(self):
        ingredients_list = get_all_ingredients()
        for item in ingredients_list:
            #temp = json.loads(item)
            #print(temp["name"])
            print(item)
