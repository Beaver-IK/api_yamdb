from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
    SignUpView,
    TokenView,
    ResendActivationCodeView
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('genres', GenreViewSet, basename='genre')
router.register('titles', TitleViewSet, basename='title')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

auth_url = [
    (path('signup/', SignUpView.as_view(),
          name='signup')),
    (path('token/', TokenView.as_view(),
          name='token')),
    (path('resend-code/', ResendActivationCodeView.as_view(),
          name='resend_code')),
]

urlpatterns = [
    path('v1/auth/', include(auth_url)),
    path('v1/', include(router.urls)),
]
