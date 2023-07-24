from django.contrib import admin

from recipes.models import (
    Tag, Recipe, Favorite, ShoppingCart, Ingredient, RecipeIngredient
)


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class TagsInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    # Не установил min num тут, потому что поле напрямую связано
    # с моделью Тегов и админка не дает оставить его пустым,
    # а дублирование приводит к необходимости указать значения в двух
    # полях формы одновременно. Таким образом, сейчас просто есть выбор
    # указать тег в связях или в поле тега, но указать его придется обязательно


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorites_count')
    list_editable = ('name', 'author')
    search_fields = ('name', 'tags', 'author')
    list_filter = ('name', 'tags', 'author')
    empty_value_display = '-пусто-'
    inlines = (IngredientsInline, TagsInline)

    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'
