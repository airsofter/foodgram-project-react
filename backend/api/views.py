from rest_framework.decorators import action
from rest_framework import (
    viewsets, exceptions, status, permissions, generics
)
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse

from api.serializers import (
    IngredientSerializer, TagSerializer,
    ReadRecipeSerializer, CreateRecipeSerializer,
    SubscriptionSerializer, ShortRecipeSerializer
)
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from api.permissions import IsAuthorOrAdminPermission
from users.models import User, Subscription
from api.filters import RecipeFilter, IngredientsFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = (IsAuthorOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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
        favorite = recipe.favorite.filter(
            user=user
        ).exists()

        if request.method == 'POST':
            if favorite:
                raise exceptions.ValidationError('Рецепт уже в избранном')
            favorite = Favorite.objects.create(user=user, recipe=recipe)
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
        in_shopping_cart = recipe.shopping_cart.filter(user=user)

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
            ingredient_recipes__recipe__shopping_cart__user=request.user
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


class SubscribtionsView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get(self, request):
        authors = User.objects.filter(author_subscription__user=request.user)
        paginate_authors = self.paginate_queryset(authors)
        serializer = self.get_serializer(paginate_authors, many=True)
        return self.get_paginated_response(serializer.data)


class SubscribtionsCreateDeleteView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        follover = request.user
        subscription = follover.user_subscription.filter(
            author=author
        ).exists()
        if not subscription:
            raise exceptions.ValidationError(
                'Вы не подписаны на этого автора'
            )
        get_object_or_404(
            Subscription,
            user=follover,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        follover = request.user
        subscription = follover.user_subscription.filter(
            author=author
        ).exists()
        if subscription:
            raise exceptions.ValidationError(
                'Вы уже подписаны на этого автора'
            )
        Subscription.objects.create(user=follover, author=author)
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
