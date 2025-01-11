from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                       SignUpView, TokenView)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('genres', GenreViewSet, basename='genre')
router.register('titles', TitleViewSet, basename='title')

auth_url = [
    (path('signup/', SignUpView.as_view(), name='signup')),
    (path('token/', TokenView.as_view(), name='token')),
]

urlpatterns = [
    path('v1/auth/', include(auth_url)),
    path('v1/', include(router.urls)),
]

"""path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),"""