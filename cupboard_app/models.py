from django.db import models
import json
# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.username} {self.email}"


class Ingredient(models.Model):
    name = models.CharField(max_length=25)
    type = models.CharField(max_length=25)

    def __str__(self):
    #    return f'{"name:":{self.name}, "type":{self.type}}'
        my_dictionary = {"name":self.name,"type":self.type}
        result = json.dumps(my_dictionary)
        return result

    #def getIngredient(self):
    #    my_dictionary = {"name":self.name,"type":self.type}
    #    return my_dictionary


class ListName(models.Model):
    listName = models.CharField(max_length=15)

    def __dict__(self):
        return f"{self.listName}"


class Measurement(models.Model):
    unit = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.unit}"


class UserListIngredients(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listName = models.ForeignKey(ListName, on_delete=models.CASCADE)
    ingredients = []

    def __str__(self):
        return f"{self.listName} - {self.user.username}"


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipeName = models.CharField(max_length=25)
    steps = []
    ingredients = []

    def __str__(self):
        return f"{self.recipeName} by {self.user.username}"
