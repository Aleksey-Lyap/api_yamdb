from rest_framework import viewsets, permissions
from rest_framework.exceptions import ParseError
from rest_framework import filters, viewsets
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .mixins import CreateDestroyListViewSet
from reviews.models import Category, Comment, Genre, Review, Title
from .permissions import (IsAdminOrReadOnly,
                          IsAuthorOrAdministratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleSerializer,
                          ModifiedTitleSerializer)


class CategoryViewSet(CreateDestroyListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateDestroyListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleSerializer
        return ModifiedTitleSerializer

    def get_queryset(self):
        """Получение Title по поиску."""
        queryset = Title.objects.all()
        params = self.request.query_params
        genre = params.get('genre')
        category = params.get('category')
        name = params.get('name')
        year = params.get('year')
        search = Q()
        if genre is not None:
            search &= Q(genre__slug=genre)
        if category is not None:
            search &= Q(category__slug=category)
        if name is not None:
            search &= Q(name=name)
        if year is not None:
            search &= Q(year=year)
        return queryset.filter(search)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdministratorOrReadOnly,)

    def get_queryset(self):
        """Получение списка отзывов."""
        title_id = self.kwargs['title_pk']
        title = get_object_or_404(Title, id=title_id)
        reviews = Review.objects.filter(title=title)
        return reviews

    def perform_create(self, serializer):
        """Создание нового отзыва."""
        title_id = self.kwargs['title_pk']
        title = get_object_or_404(Title, id=title_id)
        if Review.objects.filter(author=self.request.user,
                                 title=title).exists():
            raise ParseError('Можно оставлять только один отзыв')
        serializer.save(author=self.request.user,
                        title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdministratorOrReadOnly,)

    def get_queryset(self):
        """Получение списка комментариев."""
        review_id = self.kwargs['review_pk']
        review = get_object_or_404(Review, id=review_id)
        comments = Comment.objects.filter(review=review)
        return comments

    def perform_create(self, serializer):
        """Создание нового отзыва."""
        review_id = self.kwargs['review_pk']
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user,
                        review=review)
