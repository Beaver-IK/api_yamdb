from rest_framework import serializers

from review.models import Category, Genre, Title
from users.models import CustomUser, MAX_LENGTH, EMAIL_LENGTH


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

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')
        read_only_fields = ('id',)

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
    rating = serializers.FloatField(read_only=True)

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

class SignUpSerializer(serializers.Serializer):
    """Сериализатор для авторизации."""

    username = serializers.CharField(max_length=MAX_LENGTH)
    email = serializers.EmailField(max_length=EMAIL_LENGTH)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для аутентификации."""

    username = serializers.CharField(max_length=MAX_LENGTH)
    confirmation_code = serializers.CharField(max_length=36)


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        ]
