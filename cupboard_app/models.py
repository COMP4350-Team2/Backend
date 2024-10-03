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
    ingredients = models.ArrayField(
        model_container=models.EmbeddedField(
            model_container=models.JSONField(),  # Using JSONField to store the ingredient details
        ),
        null=True,
        blank=True
    )

    def __str__(self):
        if self.ingredients:
            ingredient_ids = [ingredient['ingredientId'] for ingredient in self.ingredients]
            unit_ids = [ingredient['unitId'] for ingredient in self.ingredients]

            # Fetch all ingredients and measurements at once
            ingredients_dict = {ing.id: ing.name for ing in Ingredient.objects.filter(id__in=ingredient_ids)}
            measurements_dict = {unit.id: unit.unit for unit in Measurement.objects.filter(id__in=unit_ids)}

            # Construct the string representation
            ingredients_str = ", ".join([
                f"{ingredients_dict[ingredient['ingredientId']]} (Amount: {ingredient['amount']}, Unit: {measurements_dict[ingredient['unitId']]})"
                for ingredient in self.ingredients
            ])
        else:
            ingredients_str = "No ingredients"

        return f"{self.listName} - {self.user.username}: {ingredients_str}"
    
class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_list_ingredients')
    recipeName = models.CharField(max_length=100,unique=True)
    steps = models.ArrayField(
        model_container=models.EmbeddedField(
            model_container=models.JSONField(),  # Each step is a simple string
        ),
        null=True,
        blank=True
    )
    ingredients = models.ArrayField(
        model_container=models.EmbeddedField(
            model_container=models.JSONField(),  # Using JSONField to store the ingredient details
        ),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.recipeName} by {self.user.username}"