from django.contrib import admin

from recipes.models import (
    Tag, Recipe, RecipeIngredient, Favorite, ShoppingCart, Ingredient
)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorites_count')
    list_editable = ('name', 'author')
    search_fields = ('name', 'tags', 'author')
    list_filter = ('name', 'tags', 'author')
    empty_value_display = '-пусто-'

    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite, FavoritesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
