from datetime import datetime

from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import CustomUser, MAX_LENGTH, EMAIL_LENGTH, MESSAGE
from api.utils import NotMeValidator


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории."""

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id',)


class CategoryListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для списка и создания категорий без поля id."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра."""

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id',)


class GenreListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для списка и создания жанров без поля id."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения."""

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
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')
        read_only_fields = ('id',)


class TitleListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для списка и создания жанров без поля id."""

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
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')
        read_only_fields = ('id',)

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список жанров ' 'не может ' 'быть пустым.'
            )
        return value

    def validate_year(self, value):
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска произведения не может превышать '
                f'текущий год ({current_year}).'
            )
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        genres = validated_data.pop('genre', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if genres is not None:
            instance.genre.set(genres)
        instance.save()
        return instance


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения с полем rating."""

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
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
            'rating',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get("description") is None:
            representation["description"] = ""
        return representation


class BaseAuthSerializer(serializers.Serializer):
    """Базовый сериализатор для регистрации и аутентификации."""

    username = serializers.CharField(
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


class SignUpSerializer(BaseAuthSerializer):
    """Сериализатор для авторизации."""

    email = serializers.EmailField(max_length=EMAIL_LENGTH)


class TokenSerializer(BaseAuthSerializer):
    """Сериализатор для аутентификации."""

    confirmation_code = serializers.CharField(max_length=36)


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    # role = role = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        read_only_fields = ('role',)


class ForAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')

    def validate_score(self, value):
        if value is None:
            raise serializers.ValidationError('Поле "score" обязательно для заполнения.')
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка должна быть в диапазоне от 1 до 10.')
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = request.user
            if Review.objects.filter(title_id=title_id, author=author).exists():
                raise ValidationError('Вы уже оставили отзыв для этого произведения.')
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
        read_only_fields = ('id', 'author', 'pub_date')
