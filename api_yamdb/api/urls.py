from django.urls import include, path
from rest_framework_nested import routers
from users.views import APIUser, UserViewSetForAdmin

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet, basename='title')

titles_router_v1 = routers.NestedSimpleRouter(
    router_v1, 'titles', lookup='title')
titles_router_v1.register('reviews', ReviewViewSet, basename='review')

reviews_router_v1 = routers.NestedSimpleRouter(
    titles_router_v1, 'reviews', lookup='review')
reviews_router_v1.register('comments', CommentViewSet, basename='comment')

router_v1.register('users', UserViewSetForAdmin, basename='users')

urlpatterns = [
    path('v1/', include(titles_router_v1.urls)),
    path('v1/', include(reviews_router_v1.urls)),
    path('v1/auth/', include('users.urls')),
    path('v1/users/me/', APIUser.as_view(), name='me'),
    path('v1/', include(router_v1.urls)),
]
