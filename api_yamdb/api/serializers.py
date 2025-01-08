from rest_framework import serializers
from reviews.models import Category, Genre, Title


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
