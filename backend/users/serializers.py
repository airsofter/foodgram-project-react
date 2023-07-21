from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer

from users.models import User
from recipes.models import Recipe


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
    # recipes = ShortRecipeSerializer(many=True)
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
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data
