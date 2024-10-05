from .models import Recipe
from .models import Ingredient


def get_all_recipes():
    return Recipe.objects.all()


def get_all_ingredients():
    return Ingredient.objects.all()
