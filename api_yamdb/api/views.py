from api.permissions import IsAdminOrReadOnly
from api.serializers import (
    CategoryListCreateSerializer,
    CategorySerializer,
    GenreListCreateSerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleSerializer,
    TitleListCreateSerializer,
)
from review.models import Category, Genre, Title

from rest_framework import filters, status, mixins, viewsets
from rest_framework.response import Response


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для управления категориями."""

    queryset = Category.objects.all().order_by('name')
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action in ['list', 'create']:
            return CategoryListCreateSerializer
        return CategorySerializer


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для управления жанрами."""

    queryset = Genre.objects.order_by('name')
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action in ['list', 'create']:
            return GenreListCreateSerializer
        return GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления произведениями."""

    queryset = Title.objects.all().order_by('name')
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleListCreateSerializer

    def get_queryset(self):
        """Фильтрует произведения по категории, жанру и году."""
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        genre = self.request.query_params.get('genre')
        year = self.request.query_params.get('year')
        name = self.request.query_params.get('name')
        if category:
            queryset = queryset.filter(category__slug=category)
        if genre:
            queryset = queryset.filter(genre__slug=genre)
        if year:
            queryset = queryset.filter(year=year)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def update(self, request, *args, **kwargs):
        """Переопределяем update, запретить PUT-запросы, разрешить PATCH."""
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
