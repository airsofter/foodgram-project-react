import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from django.db.utils import IntegrityError


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Заполнение модели ингредиентов запущено')
        with open('data/ingredients.csv', 'r', encoding='UTF-8') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    Ingredient.objects.create(
                        name=row[0],
                        measurement_unit=row[1],
                    )
                except IntegrityError:
                    print(f'{row[0]} already exists')

        print('Заполнение модели ингредиентов завершено')
