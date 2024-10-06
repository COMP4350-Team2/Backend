from django.test import TestCase
from .models import Ingredient
from .queries import get_all_ingredients
from .views import get_all_ingredients_worker as views_get_all_ingredients
from django.http import HttpRequest
import json

# Create your tests here.
class TestIngredients(TestCase):
    def setUp(self):
        Ingredient.objects.create(name="testing", type="TEST")

    def test_get_all_ingredients(self):
        ingredients_list = get_all_ingredients()
        for item in ingredients_list:
            print(item)

class TestAPIs(TestCase):
    def setUp(self):
        pass
    
    def test_get_all_ingredients(self):
        all_ingredients = views_get_all_ingredients(mockData = ['{"Name":"pickels", "Type":"Yummy"}', '{"Name":"apples", "Type":"fruit"}', '{"Name":"tomato", "Type":"vegi-fluid"}'])
        #print("Response from views is:" + str(json.loads(all_ingredients.content)))
        self.assertTrue(json.loads(all_ingredients.content) == {'result': ['{"Name":"pickels", "Type":"Yummy"}', '{"Name":"apples", "Type":"fruit"}', '{"Name":"tomato", "Type":"vegi-fluid"}']})