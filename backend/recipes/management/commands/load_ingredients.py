import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV-файла'

    def handle(self, *args, **options):
        csv_path = settings.BASE_DIR / 'data' / 'ingredients.csv'
        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {csv_path}')
            )
            return
        ingredients = []
        with open(csv_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    continue
                name, measurement_unit = row[0], row[1]
                ingredients.append(
                    Ingredient(
                        name=name,
                        measurement_unit=measurement_unit,
                    )
                )
        Ingredient.objects.bulk_create(
            ingredients,
            ignore_conflicts=True,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Ингредиенты загружены. '
                f'Всего в базе: {Ingredient.objects.count()}'
            )
        )
