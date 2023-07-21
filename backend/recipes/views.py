from rest_framework.decorators import action
from rest_framework import viewsets, filters, exceptions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.db.models import Sum
from django.http import HttpResponse

from recipes.serializers import (
    IngredientSerializer, TagSerializer,
    ReadRecipeSerializer, CreateRecipeSerializer,
)
from users.serializers import ShortRecipeSerializer
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from recipes.permissions import IsAuthorOrAdminPermission


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = (IsAuthorOrAdminPermission,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ReadRecipeSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete'),
        detail=True,
        serializer_class=ShortRecipeSerializer
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        favorite = recipe.recipe_favorite.filter(
            user=user
        ).exists()

        if request.method == 'POST':
            if favorite:
                raise exceptions.ValidationError('Рецепт уже в избранном')
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            print(type(favorite))
            serializer = self.get_serializer(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not favorite:
            raise exceptions.ValidationError(
                'Рецепт не находится в избранном'
            )
        get_object_or_404(Favorite, user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
        serializer_class=ShortRecipeSerializer
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        in_shopping_cart = recipe.recipe_shopping.filter(user=user)

        if request.method == 'POST':
            if in_shopping_cart:
                raise exceptions.ValidationError('Рецепт уже в списке покупок')
            add_to_cart = ShoppingCart.objects.create(
                user=user, recipe=recipe
            )
            serializer = self.get_serializer(add_to_cart.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not in_shopping_cart:
            raise exceptions.ValidationError(
                'Рецепт не находится в списке покупок'
            )
        get_object_or_404(ShoppingCart, user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthorOrAdminPermission,)
    )
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            ingredient_recipes__recipe__recipe_shopping__user=request.user
        ).values(
            'name', 'measurement_unit'
        ).annotate(
            amount=Sum('ingredient_recipes__amount')
        )

        text = 'Список покупок:\n'
        for ingredient in ingredients:
            text += (
                f'{ingredient["name"]}, {ingredient["amount"]}'
                f'{ingredient["measurement_unit"]}\n'
            )

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-cart.txt'
        )
        return response
