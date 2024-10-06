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
        Ingredient.objects.create(name="testing2", type="TEST2")
    def test_get_all_ingredients(self):
        ingredients_list = get_all_ingredients()
        for item in ingredients_list:
            #temp = json.loads(item)
            #print(temp["name"])
            print(item)

class TestAPIs(TestCase):
    def setUp(self):
        pass
    
    def test_get_all_ingredients(self):
        all_ingredients = views_get_all_ingredients(mockData = ['{"name":"pickels", "type":"Yummy"}', '{"name":"apples", "type":"fruit"}', '{"name":"tomato", "type":"vegi-fluid"}'])
        #print("Response from views is:" + str(json.loads(all_ingredients.content)))
        self.assertTrue(json.loads(all_ingredients.content) == {'result': ['{"name":"pickels", "type":"Yummy"}', '{"name":"apples", "type":"fruit"}', '{"name":"tomato", "type":"vegi-fluid"}']})