from api.permissions import IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
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
    ResendCodeSerializer
)
from reviews.models import Category, Genre, Title, Review
from api.utils import send_activation_email
from users.models import CustomUser
from users.authentication import generate_token

from django.shortcuts import get_object_or_404
from rest_framework import filters, status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from datetime import timezone, datetime


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


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin]
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Review.objects.all()

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(title=title, author=self.request.user)
        title.update_average_rating()


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)


class SignUpView(APIView):
    """Класс представления для регистрации и получения кода подтверждения."""

    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Этот email уж занят')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Этот username уже используется.')
        user = CustomUser.objects.create_user(username=username, email=email)
        user.generate_code()
        user.save()
        send_activation_email(user, request)
        return Response(
            {'email': user.email, 'username': user.username
            }, 
            status=status.HTTP_200_OK)


class TokenView(APIView):
    """Класс представления для аутентификации."""

    permission_classes = [AllowAny]
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        code = serializer.validated_data['confirmation_code']
        try:
            user = CustomUser.objects.get(username=username,
                                          activation_code=code)
        except CustomUser.DoesNotExist:
            raise NotFound('Неверный код активации или имя пользователя')
        if (not user.validity_code or 
            datetime.now(timezone.utc) > user.validity_code
        ):
            raise NotFound('Срок действия кода истек.')
        user.is_active = True
        user.clear_code()
        user.save()
        token = generate_token(user)
        return Response({'token': token}, status=status.HTTP_200_OK)


class ResendActivationCodeView(APIView):
    """Класс представления, для повторной отправки кода подтверждения."""

    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        try:
          user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
          raise NotFound('Пользователь не существует.')
        user.generate_code()
        user.save()
        send_activation_email(user, request)
        return Response({'message': 'Новый код отправлен на почту'},
                        status=status.HTTP_200_OK)
