from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.relations import SlugRelatedField

from api.utils import NotMeValidator, already_use
from reviews.models import Category, Genre, Title, Comment, Review
from users.models import MAX_LENGTH, EMAIL_LENGTH, MESSAGE

User = get_user_model()

# =====================================
# Константы для повторяющихся полей
# =====================================
CATEGORY_GENRE_FIELDS = ('id', 'name', 'slug')
READ_ONLY_ID = ('id',)
TITLE_FIELDS = ('id', 'name', 'year', 'description', 'category', 'genre')

# Дополнительные переменные (в сериализаторы профиля, отзывов и комментов).
READ_ONLY_ID_AUTHOR_PUB_DATE = ('id', 'author', 'pub_date')
USER_FIELDS = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


# =====================================
# Вспомогательные функции
# =====================================
def validate_year_not_exceed_current(value: int) -> int:
    """Проверяет, что год не превышает текущий год."""
    current_year = datetime.now().year
    if value > current_year:
        raise serializers.ValidationError(
            'Год выпуска произведения не может '
            f'превышать текущий год ({current_year}).'
        )
    return value


def validate_not_empty(value, field_name: str = 'поле') -> None:
    """Проверяет, что переданное значение не пустое."""
    if not value:
        raise serializers.ValidationError(
            f'Список {field_name} ' 'не может быть пустым.'
        )
    return value


def update_instance_fields(instance, validated_data: dict):
    """Обновляет поля объекта на основе validated_data и сохраняет."""
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance


# =====================================
# Поле USERNAME_FIELD
# =====================================
USERNAME_FIELD = serializers.CharField(
    max_length=MAX_LENGTH,
    validators=[
        RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=MESSAGE,
            code='invalid_username',
        ),
        NotMeValidator(),
    ],
)


# =====================================
# Category Serializers
# =====================================
class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории."""

    class Meta:
        model = Category
        fields = CATEGORY_GENRE_FIELDS
        read_only_fields = READ_ONLY_ID


class CategoryListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для списка и создания категорий без поля id."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


# =====================================
# Genre Serializers
# =====================================
class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра."""

    class Meta:
        model = Genre
        fields = CATEGORY_GENRE_FIELDS
        read_only_fields = READ_ONLY_ID


class GenreListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для списка и создания жанров без поля id."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


# =====================================
# Title Serializers
# =====================================
class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения (базовый)."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=True,
    )
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
        required=True,
    )

    class Meta:
        model = Title
        fields = TITLE_FIELDS
        read_only_fields = READ_ONLY_ID


class TitleListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для списка и создания произведений без поля id."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=True,
    )
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
        required=True,
    )
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Title
        fields = TITLE_FIELDS
        read_only_fields = READ_ONLY_ID

    def validate_genre(self, value):
        """Проверяет, что список жанров не пуст."""
        return validate_not_empty(value, 'жанров')

    def validate_year(self, value):
        """Проверяет, что год произведения не превышает текущий."""
        return validate_year_not_exceed_current(value)

    def create(self, validated_data):
        """Создаёт произведение и устанавливает жанры."""
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        """Обновляет произведение и жанры при необходимости."""
        genres = validated_data.pop('genre', None)
        instance = update_instance_fields(instance, validated_data)
        if genres is not None:
            instance.genre.set(genres)
        return instance


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения с полем рейтинга."""

    category = CategoryListCreateSerializer(read_only=True)
    genre = GenreListCreateSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    class Meta:
        model = Title
        fields = (*TITLE_FIELDS, 'rating')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get("description") is None:
            representation["description"] = ""
        return representation


# ==============================
# Базовые сериализаторы для аутентификации и регистрации
# ==============================
class BaseAuthSerializer(serializers.Serializer):
    """Базовый сериализатор для регистрации и аутентификации."""

    username = USERNAME_FIELD


class SignUpSerializer(BaseAuthSerializer):
    """Сериализатор для авторизации."""

    email = serializers.EmailField(max_length=EMAIL_LENGTH)

    def validate(self, attrs):
        return already_use(attrs)


class TokenSerializer(BaseAuthSerializer):
    """Сериализатор для аутентификации."""

    confirmation_code = serializers.CharField(max_length=36)

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs['username'])
            confirmation_code = attrs['confirmation_code']
        except User.DoesNotExist:
            raise NotFound(dict(username='Пользователь не существует'))
        except KeyError as e:
            raise ValidationError(e)
        if user.activation_code != confirmation_code:
            raise ValidationError(
                dict(confirmation_code='Неверный код подтверждения')
            )
        return attrs


# ==============================
# Сериализаторы профиля
# ==============================
class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    username = USERNAME_FIELD

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        read_only_fields = ('role',)

    def validate(self, attrs):
        return already_use(attrs)


class ForAdminSerializer(serializers.ModelSerializer):

    username = USERNAME_FIELD

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate(self, attrs):
        return already_use(attrs)


# ==============================
# Review и Comment Serializers
# ==============================
class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')
        read_only_fields = READ_ONLY_ID_AUTHOR_PUB_DATE

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10.'
            )
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = request.user
            if Review.objects.filter(
                title_id=title_id,
                author=author
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв для этого произведения.'
                )
            if 'score' not in data:
                raise serializers.ValidationError(
                    {'score': 'Поле "score" обязательно для заполнения.'}
                )
        return data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['title_id'] = self.context['view'].kwargs.get(
            'title_id',
        )
        return Review.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = READ_ONLY_ID_AUTHOR_PUB_DATE
