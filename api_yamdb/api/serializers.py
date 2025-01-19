from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.relations import SlugRelatedField

from api import constants as ca
from api import utils
from api.fields import USERNAME_FIELD
from api.utils import validate_not_empty, validate_year_not_exceed_current
from reviews.models import Category, Comment, Genre, Review, Title
from users import constants as cu

User = get_user_model()


# =====================================
# Category Serializers
# =====================================
class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории."""

    class Meta:
        model = Category
        fields = ca.CATEGORY_GENRE_FIELDS
        read_only_fields = ca.READ_ONLY_ID


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
        fields = ca.CATEGORY_GENRE_FIELDS
        read_only_fields = ca.READ_ONLY_ID


class GenreListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для списка и создания жанров без поля id."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


# =====================================
# Title Serializers
# =====================================
class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования Title."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=True,
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
        required=True,
    )
    description = serializers.CharField(required=False, allow_blank=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ca.TITLE_FIELDS
        read_only_fields = ('id',)

    def validate_genre(self, value):
        return validate_not_empty(value, 'жанров')

    def validate_year(self, value):
        return validate_year_not_exceed_current(value)

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения с вложенными сериализаторами и рейтингом."""

    category = CategoryListCreateSerializer(read_only=True)
    genre = GenreListCreateSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ca.TITLE_FIELDS

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('description') is None:
            representation['description'] = ''
        if representation.get('rating') is None:
            representation['rating'] = None
        return representation


# ==============================
# Базовые сериализаторы для аутентификации и регистрации
# ==============================
class BaseAuthSerializer(serializers.Serializer):
    """Базовый сериализатор для регистрации и аутентификации."""

    username = USERNAME_FIELD


class SignUpSerializer(BaseAuthSerializer):
    """Сериализатор для авторизации."""

    email = serializers.EmailField(max_length=cu.EMAIL_LENGTH)

    def validate(self, attrs):
        return utils.already_use(attrs)


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
        if user.confirmation_code != confirmation_code:
            raise ValidationError(dict(
                confirmation_code='Неверный код подтверждения'
            )
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
        fields = ca.USER_FIELDS
        read_only_fields = ('role',)

    def validate(self, attrs):
        return utils.already_use(attrs)


class ForAdminSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя с правами администратора."""

    username = USERNAME_FIELD

    class Meta:
        model = User
        fields = ca.USER_FIELDS

    def validate(self, attrs):
        return utils.already_use(attrs)


# ==============================
# Review и Comment Serializers
# ==============================
class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')
        read_only_fields = ca.READ_ONLY_ID_AUTHOR_PUB_DATE

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = request.user
            if Review.objects.filter(title_id=title_id,
                                     author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв для этого произведения.'
                )
            if 'score' not in data:
                raise serializers.ValidationError(
                    {'score': 'Поле "score" обязательно для заполнения.'}
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ca.READ_ONLY_ID_AUTHOR_PUB_DATE
