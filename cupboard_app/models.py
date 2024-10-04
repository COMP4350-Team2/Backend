from django.db import models
from bson import ObjectId

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=100,unique=True)
    email = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return f"{self.username} {self.email}"
    
class Ingredient(models.Model):
    name = models.CharField(max_length=100,unique=True)
    type = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return f"{self.name} {self.type}"

class ListName(models.Model):
    listName = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return f"{self.listName}"

class Measurement(models.Model):
    unit = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return f"{self.unit}"
    
class UserListIngredients(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_list_ingredients')
    listName = models.ForeignKey(ListName, on_delete=models.CASCADE, related_name='user_lists')
    
    # Use JSONField to store the ingredients, amounts, and units in a single field
    ingredients = models.JSONField(null=True, blank=True)  # Store as a list of dictionaries

    def __str__(self):
        if self.ingredients:
            # Extract the ingredient details from the JSON field
            ingredients_str = ", ".join([
                f"{ingredient['name']} (Amount: {ingredient['amount']}, Unit: {ingredient['unit']})"
                for ingredient in self.ingredients
            ])
        else:
            ingredients_str = "No ingredients"

        return f"{self.listName} - {self.user.username}: {ingredients_str}"
    
class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_recipes')
    recipeName = models.CharField(max_length=100, unique=True)

    # Use JSONField to store steps as a list of strings
    steps = models.JSONField(null=True, blank=True)  # Store steps as a list of strings

    # Use JSONField to store ingredients as a list of dictionaries
    ingredients = models.JSONField(null=True, blank=True)  # Store ingredients as a list of dictionaries

    def __str__(self):
        return f"{self.recipeName} by {self.user.username}"