import csv
from django.core.management.base import BaseCommand, CommandError
from reviews.models import Category, Comment, Genre, Review, Title
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

# Словарь, в котором указывается, для каких моделей
# нужно преобразовывать внешние ключи
# ключами являются классы моделей, а значениями — словарь, где:
#   ключ: имя поля (как оно указано в CSV)
#   значение: соответствующая модель для преобразования значения (ID -> объект)
FK_FIELDS = {
    Comment: {'author': CustomUser, 'review': Review},
    Title: {'category': Category},
    Review: {'author': CustomUser, 'title': Title},
    # Для Category, Genre, CustomUser не требуется преобразования
}


def import_csv(file_path, model_class):
    """Импорт CSV для модели."""
    fk_map = FK_FIELDS.get(model_class, {})
    instances = []
    with open(file_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Преобразуем внешние ключи, если они описаны в fk_map
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


# Карта соответствия имен моделей (из параметров команды) и классов моделей
MODEL_MAP = {
    'comment': Comment,
    'category': Category,
    'genre': Genre,
    'review': Review,
    'title': Title,
    'user': CustomUser,
}


class Command(BaseCommand):
    """Команда для импорта CSV данных в базу."""

    help = 'Импорт данных из CSV в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            type=str,
            help='Имя модели или специального типа импорта',
        )
        parser.add_argument(
            'file_path',
            type=str,
            help='Путь к CSV файлу',
        )

    def handle(self, *args, **options):
        model_name = options['model'].lower()
        file_path = options['file_path']

        try:
            if model_name == 'reviews_title_genre':
                import_title_genre_links(file_path)
            else:
                if model_name not in MODEL_MAP:
                    raise CommandError(f'Модели "{model_name}" нет.')
                model_class = MODEL_MAP[model_name]
                import_csv(file_path, model_class)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно импортированы данные в модель "{model_name}".'
                )
            )
        except Exception as e:
            raise CommandError(f'Ошибка при импорте данных: {e}')
