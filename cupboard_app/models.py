from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(min_length=1,max_length=30,unique=True)
    email = models.CharField(min_length=1,max_length=30,unique=True)

    def __str__(self):
        return f"{self.username} {self.email}"
    
class Ingredient(models.Model):
    name = models.CharField(min_length=1,max_length=25)
    type = models.CharField(min_length=1,max_length=25)

    def __str__(self):
        return f"{self.name} {self.type}"

class ListName(models.Model):
    listName = models.CharField(min_length=1,max_length=15)

    def __str__(self):
        return f"{self.listName}"

class Measurement(models.Model):
    unit = models.CharField(min_length=1,max_length=15,unique=True)

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
    recipeName = models.CharField(min_length=1,max_length=25)
    steps = []
    ingredients = []

    def __str__(self):
        return f"{self.recipeName} by {self.user.username}"