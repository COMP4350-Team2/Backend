import json

from django.db import models
from django.core.exceptions import ValidationError


class Message():
    # Not a database model, object for messages serializer
    def __init__(self, message=''):
        self.message = message


class Ingredient(models.Model):
    name = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=30)

    def __str__(self):
        my_dictionary = {'name': self.name, 'type': self.type}
        result = json.dumps(my_dictionary)
        return result


class ListName(models.Model):
    list_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.list_name}'


class Measurement(models.Model):
    unit = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.unit}'


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=100, unique=True)

    def __str__(self):
        my_dictionary = {'username': self.username, 'email': self.email}
        result = json.dumps(my_dictionary)
        return result


class UserListIngredients(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list_name = models.ForeignKey(ListName, on_delete=models.CASCADE)
    ingredients = models.JSONField()

    def __str__(self):
        return f'{self.user.username} - {self.list_name.list_name}'


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_name = models.CharField(max_length=50)
    steps = models.JSONField()
    ingredients = models.JSONField()

    def __str__(self):
        return f'{self.recipe_name} by {self.user.username}'


class CustomIngredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=30)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        if type(self).objects.filter(
            user__username=self.user.username,
            name=self.name
        ).exists():
            raise ValidationError('Ingredient already exists for user.')

    def __str__(self):
        my_dictionary = {'name': self.name, 'type': self.type}
        result = json.dumps(my_dictionary)
        return result
