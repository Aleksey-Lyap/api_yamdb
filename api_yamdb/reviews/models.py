from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import YearValidator


class User(AbstractUser):
    ROLES = (("user", "User"),
             ("moderator", "Moderator"),
             ("admin", "Admin"))
    email = models.EmailField(_('email address'),
                              blank=False,
                              unique=True,
                              max_length=254)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default='user')

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField(db_index=True,
                                            validators=[YearValidator()])
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='titles')

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ])

    class Meta:
        constraints = [
            models.UniqueConstraint(name='author_title_unique',
                                    fields=['author_id', 'title_id'])
        ]
        permissions = [
            ('change_own_review', 'Can change own review'),
            ('delete_own_review', 'Can delete own review'),
        ]

    def __str__(self):
        return str(self.title)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        permissions = [
            ('change_own_comment', 'Can change own comment'),
            ('delete_own_comment', 'Can delete own comment'),
        ]

    def __str__(self):
        return str(self.text)
