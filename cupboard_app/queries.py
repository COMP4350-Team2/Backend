from .models import Recipe
from .models import Ingredient
def get_all_recipes():
    """Retrieve all recipes."""
    return Recipe.objects.all()

def get_all_ingredients():
    """Retrieve all ingredients."""
    return Ingredient.objects.all()