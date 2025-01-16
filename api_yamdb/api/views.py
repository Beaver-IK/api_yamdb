from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from api.permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
    IsAdminOnly
)
from api.serializers import (
    CategoryListCreateSerializer,
    CategorySerializer,
    GenreListCreateSerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleListCreateSerializer,
    ReviewSerializer,
    CommentSerializer,
    SignUpSerializer,
    TokenSerializer,
    ProfileSerializer,
    ForAdminSerializer,
)
from api.utils import send_activation_email

from reviews.models import Category, Genre, Title, Review

from users.authentication import generate_jwt_token

User = get_user_model()


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

    def build_filter_kwargs(self):
        """Формирует словарь фильтров по переданным параметрам."""
        param_map = {
            'category': 'category__slug',
            'genre': 'genre__slug',
            'year': 'year',
            'name': 'name__icontains',
        }
        filters_dict = {}
        for query_param, filter_field in param_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                filters_dict[filter_field] = value
        return filters_dict

    def get_queryset(self):
        queryset = super().get_queryset()
        filters_dict = self.build_filter_kwargs()
        if filters_dict:
            queryset = queryset.filter(**filters_dict)
        return queryset

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def perform_response(self, instance, status_code):
        read_serializer = TitleReadSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status_code)

    def create(self, request, *args, **kwargs):
        write_serializer = TitleListCreateSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        write_serializer.is_valid(raise_exception=True)
        instance = self.perform_create(write_serializer)
        return self.perform_response(instance, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        write_serializer = TitleListCreateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        write_serializer.is_valid(raise_exception=True)
        instance = self.perform_update(write_serializer)
        return self.perform_response(instance, status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Review.objects.all().order_by('-pub_date')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id).order_by('-pub_date')

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(title=title, author=self.request.user)
        title.update_average_rating()


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями."""

    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )

    def get_queryset(self):
        return self.get_review().comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)


class SignUpView(APIView):
    """Класс представления для регистрации и получения кода подтверждения."""

    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email, username=username)
            user.generate_code()
            user.save()
            send_activation_email(user, request)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, email=email)
            user.generate_code()
            user.save()
            send_activation_email(user, request)
        return Response(
            dict(email=user.email, username=user.username),
            status=status.HTTP_200_OK,
        )


class TokenView(APIView):
    """Класс представления для аутентификации."""

    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        token = generate_jwt_token(user)
        return Response({'token': token}, status=status.HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    """Вьюсет для управления пользователей."""

    queryset = User.objects.all().order_by('username')
    permission_classes = [IsAuthenticated, IsAdminOnly]
    serializer_class = ForAdminSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me',
    )
    def get_user(self, request):
        if request.user.role == 'admin':
            serializer_class = ForAdminSerializer
        else:
            serializer_class = ProfileSerializer
        if request.method == 'PATCH':
            serializer = serializer_class(
                request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
