from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views as v

router = DefaultRouter()
router.register('categories', v.CategoryViewSet, basename='category')
router.register('genres', v.GenreViewSet, basename='genre')
router.register('titles', v.TitleViewSet, basename='title')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    v.ReviewViewSet,
    basename='review'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    v.CommentViewSet,
    basename='comment'
)
router.register('users', v.UsersViewSet, basename='users')

auth_url = [
    (path('signup/', v.SignUpView.as_view(),
          name='signup')),
    (path('token/', v.TokenView.as_view(),
          name='token')),
]

urlpatterns = [
    path('v1/auth/', include(auth_url)),
    path('v1/', include(router.urls)),
]
