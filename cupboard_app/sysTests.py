import os
import json
import subprocess

from tests import get_test_access_token
from cupboard_app.models import (
    Ingredient
)

# System Test for get all ingredients api
def test_get_all_ing_api():
    # Populates test db instance with setup values
    Ingredient.objects.create(name="test_ingredient1", type="test_type1")
    Ingredient.objects.create(name="test_ingredient2", type="test_type1")

    # Sends GET request to the  get all ingredients api
    result = subprocess.check_output("curl localhost:" + os.getenv('DJANGO_PORT') +" -H HTTP_AUTHORIZATION=Bearer {}".format(get_test_access_token()), shell=True, text=True)
    print(result)

    # ensures received value from the request is in proper format in with expected information
    assert(json.loads(result) ==
        {
            'result': [
                {'name': 'test_ingredient1', 'type': 'test_type1'},
                {'name': 'test_ingredient2', 'type': 'test_type1'}
            ]
        }
    )

    # Cleans up objects in test db instance
    Ingredient.objects.filter(name="test_ingredient1").delete()
    Ingredient.objects.filter(name="test_ingredient2").delete()

# Runs all 
def run_all_system_tests():
    test_get_all_ing_api()