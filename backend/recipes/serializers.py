from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from recipes.models import (
    Ingredient, Tag,
    Recipe, RecipeIngredient,
)
from users.serializers import CustomUserSerializer
from django.db import transaction


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для GET-запросов к модели Тегов'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для GET-запросов к модели Ингредиентов'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для отображения ингредиентов в рецепте'''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit '
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class ReadRecipeSerializer(serializers.ModelSerializer):
    '''GET запросы к рецептам'''
    ingredients = IngredientsInRecipeSerializer(
        many=True, source='recipe_ingredients', read_only=True
    )
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()
    text = serializers.CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        '''Проверка наличия рецепта в избранном'''
        curent_user = self.context['request'].user
        if curent_user.is_anonymous:
            return False
        return curent_user.user_favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        '''Проверка наличия рецепта в списке покупок'''
        curent_user = self.context['request'].user
        if curent_user.is_anonymous:
            return False
        return curent_user.user_shopping.filter(recipe=obj).exists()


class CreateRecipeSerializer(ReadRecipeSerializer):
    '''POST, PATCH, DELETE запросы к рецептам'''
    ingredients = IngredientsInRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.only('id'),
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags',
            'image', 'name', 'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        with transaction.atomic():
            recipe = super().create(validated_data)

            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient_id=ingredient['ingredient']['id'],
                    amount=ingredient['amount']
                )
            return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients', [])
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if ingredients:
                instance.ingredients.clear()
                for ingredient in ingredients:
                    RecipeIngredient.objects.create(
                        recipe=instance,
                        ingredient_id=ingredient['ingredient']['id'],
                        amount=ingredient['amount']
                    )
            return instance
