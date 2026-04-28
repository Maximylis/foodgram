from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Создаёт базовые теги'

    def handle(self, *args, **options):
        tags = [
            {
                'name': 'Завтрак',
                'slug': 'breakfast',
            },
            {
                'name': 'Обед',
                'slug': 'lunch',
            },
            {
                'name': 'Ужин',
                'slug': 'dinner',
            },
        ]
        for tag in tags:
            Tag.objects.get_or_create(
                slug=tag['slug'],
                defaults={
                    'name': tag['name'],
                },
            )
        self.stdout.write(
            self.style.SUCCESS(
                f'Теги загружены. Всего в базе: {Tag.objects.count()}'
            )
        )
