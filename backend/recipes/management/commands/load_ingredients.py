import csv
import logging

from django.core.management.base import BaseCommand
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient
from django.db.utils import IntegrityError


logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.info('Заполнение модели ингредиентов запущено')
        with open('data/ingredients.csv', 'r', encoding='UTF-8') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    Ingredient.objects.create(
                        name=row[0],
                        measurement_unit=row[1],
                    )
                except IntegrityError:
                    raise ValidationError('alredy exist')

        logging.info('Заполнение модели ингредиентов завершено')
