import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comment, Genre, Review, Title

CustomUser = get_user_model()

# Константа указывающая, где по умолчанию лежат все CSV-файлы
DEFAULT_BASE_DIR = 'static/data'

# Словарь для автоматического определения,
# какие файлы относятся к каким моделям
# Ключ: имя, передаваемое в "python manage.py import_csv <model>"
# Значение: имя CSV-файла, лежащего в DEFAULT_BASE_DIR
CSV_FILES = {
    'user': 'users.csv',
    'category': 'category.csv',
    'genre': 'genre.csv',
    'title': 'titles.csv',
    'review': 'review.csv',
    'comment': 'comments.csv',
    # Специальный случай — связи Title <-> Genre
    'reviews_title_genre': 'genre_title.csv',
}

# Словарь для сопоставления названия модели и класса модели
MODEL_MAP = {
    'user': CustomUser,
    'category': Category,
    'genre': Genre,
    'title': Title,
    'review': Review,
    'comment': Comment,
    # 'reviews_title_genre' тут не указываем,
    # т.к. это особый случай (ManyToMany).
}

# Словарь, в котором описаны поля (FK) и соответствующие модели
# чтобы автоматически превращать ID в объекты
FK_FIELDS = {
    Comment: {'author': CustomUser, 'review': Review},
    Title: {'category': Category},
    Review: {'author': CustomUser, 'title': Title},
    # Category, Genre, CustomUser - без внешних ключей к другим моделям
}


def import_csv(file_path, model_class):
    """Импорт CSV для модели."""
    fk_map = FK_FIELDS.get(model_class, {})
    instances = []

    with open(file_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Преобразуем внешние ключи (ID -> объекты)
            for field_name, fk_model in fk_map.items():
                fk_id = row.pop(field_name, None)
                if fk_id not in (None, ''):
                    try:
                        row[field_name] = fk_model.objects.get(id=fk_id)
                    except fk_model.DoesNotExist:
                        raise CommandError(
                            f'{fk_model.__name__} с id={fk_id} не найден.'
                        )
            instances.append(model_class(**row))
    model_class.objects.bulk_create(instances)


def import_title_genre_links(file_path):
    """Импорт ManyToMany-связей для Title <-> Genre."""
    with open(file_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title_id = row.get('title_id')
            genre_id = row.get('genre_id')
            if not title_id or not genre_id:
                continue
            try:
                title = Title.objects.get(id=title_id)
            except Title.DoesNotExist:
                raise CommandError(f'Произведение с id={title_id} не найдено.')

            try:
                genre = Genre.objects.get(id=genre_id)
            except Genre.DoesNotExist:
                raise CommandError(f'Жанр с id={genre_id} не найден.')

            title.genre.add(genre)


class Command(BaseCommand):
    """
    Команда для импорта данных из CSV в базу.
    Примеры:
      1) Импорт всех моделей разом из папки static/data:
         python manage.py import_csv all
      2) Импорт одной модели (например, user) из csv-файла по умолчанию:
         python manage.py import_csv user
      3) Импорт одной модели (comment), указав свой путь к CSV:
         python manage.py import_csv comment /path/to/comments.csv
      4) Переопределить базовую папку, если нужно
         добавьте parser.add_argument --base_dir.
    """

    help = 'Импорт данных из CSV в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            type=str,
            help='Имя модели или "all" для импорта всех',
        )
        parser.add_argument(
            'file_path',
            type=str,
            nargs='?',  # делаем этот аргумент необязательным
            help='Путь к CSV-файлу (необязательно)',
        )
        parser.add_argument(
            '--base_dir',
            type=str,
            default=DEFAULT_BASE_DIR,
            help=f'Папка, где лежат файлы. По умолчанию: {DEFAULT_BASE_DIR}',
        )

    def handle(self, *args, **options):
        model_name = options['model'].lower()
        file_path = options.get('file_path')
        base_dir = options['base_dir']

        # Если "all", то идём по списку CSV_FILES
        if model_name == 'all':
            self.import_all(base_dir)
            return

        # Если не "all" — то одна модель
        if model_name not in CSV_FILES:
            raise CommandError(
                'Модель (или специальный ключ) '
                f'"{model_name}" не поддерживается.\n'
                f'Доступные варианты: {list(CSV_FILES.keys()) + ["all"]}'
            )

        # Определяем реальный путь к CSV-файлу
        if file_path is None:
            # Если пользователь не указал путь, берём из CSV_FILES и base_dir
            filename = CSV_FILES[model_name]
            file_path = os.path.join(base_dir, filename)

        try:
            if model_name == 'reviews_title_genre':
                # Специальная обработка ManyToMany
                import_title_genre_links(file_path)
            else:
                model_class = MODEL_MAP[model_name]
                import_csv(file_path, model_class)

            self.stdout.write(
                self.style.SUCCESS(
                    'Успешно импортированы данные ' f'для "{model_name}".'
                )
            )
        except Exception as e:
            raise CommandError(
                'Ошибка при импорте данных ' 'для ' '"{model_name}": {e}'
            )

    def import_all(self, base_dir):
        """Импортировать все модели по очереди."""
        # Список в каком порядке стоит импортировать (если нужно).
        import_order = [
            'user',
            'category',
            'genre',
            'title',
            'review',
            'comment',
            'reviews_title_genre',
        ]

        for model_name in import_order:
            filename = CSV_FILES[model_name]
            full_path = os.path.join(base_dir, filename)

            self.stdout.write(f'Импорт {model_name} из {full_path}...')
            if model_name == 'reviews_title_genre':
                import_title_genre_links(full_path)
            else:
                model_class = MODEL_MAP[model_name]
                import_csv(full_path, model_class)

            self.stdout.write(self.style.SUCCESS(f'  => OK: {model_name}'))

        self.stdout.write(self.style.SUCCESS('Все модели импортированы!'))
