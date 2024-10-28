from rest_framework import serializers

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients,
    Recipe
)
from cupboard_app.queries import (
    ADD_ACTION,
    REMOVE_ACTION
)


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class UserListIngredientsViewSerializer(serializers.Serializer):
    list_name = serializers.CharField()
    ingredient = serializers.CharField()
    amount = serializers.FloatField()
    unit = serializers.CharField()
    action = serializers.ChoiceField(choices=[ADD_ACTION, REMOVE_ACTION])


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'type']


class list_nameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListName
        fields = ['list_name']


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ['unit']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserListIngredientsSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    list_name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='list_name'
    )

    class Meta:
        model = UserListIngredients
        fields = ['user', 'list_name', 'ingredients']


class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    recipe_name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='recipe_name'
    )

    class Meta:
        model = Recipe
        fields = ['user', 'recipe_name', 'steps', 'ingredients']
