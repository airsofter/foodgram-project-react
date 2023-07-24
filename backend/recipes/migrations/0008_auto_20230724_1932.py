# Generated by Django 3.2.3 on 2023-07-24 16:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230722_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Время должно быть больше нуля'), django.core.validators.MaxValueValidator(300, 'Время не должно превышать 300 минут')], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Количество должно быть больше нуля'), django.core.validators.MaxValueValidator(1000, 'Количество не должно превышать 1000 ед.')], verbose_name='Количество ингредиентов в рецепте'),
        ),
    ]
