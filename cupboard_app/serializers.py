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


class UserListIngredientsViewSerializer(serializers.Serializer):
    username = serializers.CharField()
    list_name = serializers.CharField()
    ingredient = serializers.CharField()
    amount = serializers.FloatField()
    unit = serializers.CharField()


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'type']


class list_nameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ListName
        fields = ['list_name']


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
        fields = ['user', 'list_name', 'ingredients']


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ['user', 'recipe_name', 'steps', 'ingredients']
