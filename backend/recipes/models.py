from django.db import models
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField

from users.models import User
from foodgram.settings import LENGTH_10, LENGTH_200


class Ingredient(models.Model):
    """Класс для хранения ингредиентов в базе данных"""
    name = models.CharField(
        max_length=LENGTH_200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=LENGTH_10,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_measurement_unit_ingredient'
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Теги рецептов"""
    COLOR_PALETTE = [
        ("#FFFFFF", "white", ),
        ("#000000", "black", ),
    ]
    name = models.CharField(
        max_length=LENGTH_10,
        unique=True,
        verbose_name='Название тега'
    )
    color = ColorField(
        samples=COLOR_PALETTE,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=LENGTH_10,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты'
    )
    name = models.CharField(
        max_length=LENGTH_200,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1, 'Время должно быть больше нуля'
        )]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tag_recipes',
        verbose_name='Тег'
    )

    class Meta:
        ordering = ('-pub_date', 'name')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связи моделей рецепта и ингредиента"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов в рецепте',
        validators=[MinValueValidator(
            1, 'Количество должно быть больше нуля'
        )]
    )

    class Meta:
        ordering = ('recipe', 'ingredient')
        verbose_name = 'Связь рецепта и ингредиента'
        verbose_name_plural = 'Связи рецептов и ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (f'{self.ingredient} в количестве {self.amount}шт. '
                f'используется в рецепте {self.recipe}')


class AbstractFavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('recipe', 'user')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_Favorite_and_ShoppingCart'
            )
        ]


class Favorite(AbstractFavoriteShoppingCart):
    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        default_related_name = 'favorite'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(AbstractFavoriteShoppingCart):
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
