import csv
from django.core.management.base import BaseCommand, CommandError
from reviews.models import Category, Genre, Title


class Command(BaseCommand):
    """Команда для импорта данных из CSV в базу данных."""

    help = 'Импорт данных из CSV в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            type=str,
            help='Модель для импорта данных',
        )
        parser.add_argument(
            'file_path',
            type=str,
            help='Путь к CSV файлу',
        )

    def handle(self, *args, **kwargs):
        model_name = kwargs['model'].lower()
        file_path = kwargs['file_path']

        model_map = {
            'category': Category,
            'genre': Genre,
            'title': Title,
        }

        if model_name not in model_map:
            raise CommandError(
                f'Модель "{model_name}" не поддерживается. '
                f'Доступные модели: {", ".join(model_map.keys())}'
            )

        model = model_map[model_name]

        try:
            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                model_instances = []

                for row in reader:
                    model_instances.append(model(**row))

                model.objects.bulk_create(model_instances)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно импортированы данные в модель "{model_name}".'
                )
            )
        except Exception as e:
            raise CommandError(f'Ошибка при импорте данных: {e}')
