from rest_framework import serializers

from cupboard_app.models import (
    Ingredient,
    ListName,
    Measurement,
    User,
    UserListIngredients,
    Recipe,
    CustomIngredient
)


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class SessionSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    id_token = serializers.CharField()
    issued_time = serializers.CharField()
    expire_time = serializers.CharField()
    user_info = serializers.JSONField()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'type']


class ListNameSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Recipe
        fields = ['user', 'recipe_name', 'steps', 'ingredients']


class CustomIngredientSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = CustomIngredient
        fields = ['user', 'name', 'type']
