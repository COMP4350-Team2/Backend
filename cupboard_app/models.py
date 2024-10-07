import json

from django.db import models


# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=30)

    def __str__(self):
        my_dictionary = {"name": self.name, "type": self.type}
        result = json.dumps(my_dictionary)
        return result


class ListName(models.Model):
    listName = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.listName}"


class Measurement(models.Model):
    unit = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.unit}"


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.username} {self.email}"


class UserListIngredients(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listName = models.ForeignKey(ListName, on_delete=models.CASCADE)
    ingredients = models.JSONField()

    def __str__(self):
        return f"{self.listName} - {self.user.username}"


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipeName = models.CharField(max_length=50)
    steps = models.JSONField()
    ingredients = models.JSONField()

    def __str__(self):
        return f"{self.recipeName} by {self.user.username}"
