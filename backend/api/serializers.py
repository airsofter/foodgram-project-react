from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.core.validators import MinValueValidator
import re

from recipes.models import (
    Ingredient, Tag,
    Recipe, RecipeIngredient,
)
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return current_user.user_subscription.filter(author=author).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


class ShortRecipeSerializer(serializers.ModelSerializer):
    '''Отображение рецептов на странице подписок'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    '''Отображение авторов, на которых подписан пользователь'''
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes_count',
            'recipes'
        )

    def get_recipes_count(self, user):
        '''Подсчет количества рецептов'''
        return user.author_recipes.count()

    def get_recipes(self, author):
        recipes = Recipe.objects.filter(author=author)
        recipe_limit = self.context['request'].GET.get('recipes_limit')
        recipes = recipes[:int(recipe_limit)] if recipe_limit else recipes
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data


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
        source='ingredient.measurement_unit ',
        validators=(
            MinValueValidator(
                1,
                message='Количество должно быть больше 1 единицы'
            ),
        )
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
        return curent_user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        '''Проверка наличия рецепта в списке покупок'''
        curent_user = self.context['request'].user
        if curent_user.is_anonymous:
            return False
        return curent_user.shopping_cart.filter(recipe=obj).exists()


class CreateRecipeSerializer(ReadRecipeSerializer):
    '''POST, PATCH, DELETE запросы к рецептам'''
    ingredients = IngredientsInRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.only('id'),
        many=True
    )
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='Время приготовления должно быть больше 1 минуты'
            ),
        )
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags',
            'image', 'name', 'text',
            'cooking_time',
        )

    def check_ingredients_and_tags(self, obj, string):
        for item in obj:
            if obj.count(item) > 1:
                raise serializers.ValidationError(
                    f'У рецепта не может быть одинаковых {string}'
                )
            return

    def validate_name(self, obj):
        from sys import stderr
        print(obj, file=stderr)
        if not re.match(r"\w*[a-zA-Zа-яА-Я]\w*", obj):
            raise serializers.ValidationError(
                'Название должно содержать буквы и начинаться с буквы'
            )
        return obj

    def validate(self, attrs):
        if not self.partial:
            if 'recipe_ingredients' not in attrs:
                raise serializers.ValidationError('Выберите ингредиенты')
            if 'tags' not in attrs:
                raise serializers.ValidationError('Выберите теги')
            self.check_ingredients_and_tags(
                attrs['recipe_ingredients'], 'ингредиентов'
            )
            self.check_ingredients_and_tags(attrs['tags'], 'тегов')

        if 'recipe_ingredients' in attrs:
            self.check_ingredients_and_tags(
                attrs['recipe_ingredients'], 'ингредиентов'
            )
        if 'tags' in attrs:
            self.check_ingredients_and_tags(attrs['tags'], 'тегов')
        return attrs

    def create_ingredients(self, ingredients, recipes):
        new_ingredients = []
        for ingredient in ingredients:
            new_ingredient = RecipeIngredient(
                recipe=recipes,
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
            new_ingredients.append(new_ingredient)
        return RecipeIngredient.objects.bulk_create(new_ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        instance = super().update(instance, validated_data)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
