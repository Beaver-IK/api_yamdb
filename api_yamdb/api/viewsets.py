from rest_framework import mixins, viewsets, filters
from api import permissions as pms


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет для категорий и жанров."""

    permission_classes = [pms.IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
