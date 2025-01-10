from rest_framework import serializers
from reviews.models import Category, Genre, Title
from users.models import CustomUser, MAX_LENGTH, EMAIL_LENGTH


class SignUpSerialiser(serializers.Serializer):
    username = serializers.CharField(max_length=MAX_LENGTH)
    email = serializers.EmailField(max_length=EMAIL_LENGTH)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=36)


class ProfileSerializer(serializers.ModelSerializer):
     class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        ]


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории."""

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра."""

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')
        read_only_fields = ('id',)
