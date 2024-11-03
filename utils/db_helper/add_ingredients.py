import json
import os
from cupboard_app.queries import (
    create_ingredient
)


filepath = os.getenv('JSON_PATH')
with open(filepath, 'r', encoding='utf8') as file:
    data = json.load(file)

    for i in data:
        if i['food_group'] is not None:
            create_ingredient(i['name'], i['food_group'])
        else:
            create_ingredient(i['name'], 'Miscellaneous')


