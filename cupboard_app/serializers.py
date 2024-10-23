from rest_framework import serializers

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients,
    Recipe
)


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'type']


class ListNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ListName
        fields = ['listName']


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measurement
        fields = ['unit']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserListIngredientsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserListIngredients
        fields = ['user', 'listName', 'ingredients']


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ['user', 'recipeName', 'steps', 'ingredients']
