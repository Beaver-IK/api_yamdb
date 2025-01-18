from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api import permissions as pms
from api import serializers as sz
from api.filters import TitleFilter
from api.utils import send_activation_email
from api.viewsets import ListCreateDestroyViewSet
from reviews.models import Category, Genre, Review, Title
from users.authentication import generate_jwt_token

User = get_user_model()


class CategoryViewSet(ListCreateDestroyViewSet):
    """Вьюсет для управления категориями."""

    queryset = Category.objects.order_by('name')
    serializer_class = sz.CategoryListCreateSerializer
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    """Вьюсет для управления жанрами."""

    queryset = Genre.objects.order_by('name')
    serializer_class = sz.GenreListCreateSerializer
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet): 
    """Вьюсет для управления произведениями.""" 
 
    queryset = Title.objects.order_by('name') 
    permission_classes = [pms.IsAdminOrReadOnly] 
    filter_backends = [DjangoFilterBackend] 
    filterset_class = TitleFilter 
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options'] 
 
    def get_serializer_class(self): 
        if self.action in ('list', 'retrieve'): 
            return sz.TitleReadSerializer 
        return sz.TitleWriteSerializer 
 
    def perform_create(self, serializer): 
        serializer.save() 
 
    def perform_update(self, serializer): 
        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""

    serializer_class = sz.ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        pms.IsAuthorOrModeratorOrAdmin,
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Review.objects.order_by('-pub_date')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews_set.order_by('-pub_date')

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями."""

    serializer_class = sz.CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        pms.IsAuthorOrModeratorOrAdmin,
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )

    def get_queryset(self):
        return self.get_review().comments.order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)


class SignUpView(APIView):
    """Класс представления для регистрации и получения кода подтверждения."""

    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        serializer = sz.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        user = User.objects.get_or_create(email=email, username=username)[0]
        user.generate_code()
        user.save()
        send_activation_email(user)
        return Response(
            dict(email=user.email, username=user.username),
            status=status.HTTP_200_OK,
        )


class TokenView(APIView):
    """Класс представления для аутентификации."""

    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        serializer = sz.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        user.is_active = True
        user.save()
        token = generate_jwt_token(user)
        user.clear_code()
        return Response({'token': token}, status=status.HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    """Вьюсет для управления пользователей."""

    queryset = User.objects.all().order_by('username')
    permission_classes = [IsAuthenticated, pms.IsAdminOnly]
    serializer_class = sz.ForAdminSerializer
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
            serializer_class = sz.ForAdminSerializer
        else:
            serializer_class = sz.ProfileSerializer
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
