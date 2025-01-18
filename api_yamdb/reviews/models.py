from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews import constants as cr

User = get_user_model()


class RCBase(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_related',
        verbose_name='автор',
    )
    text = models.TextField('текст',)
    pub_date = models.DateTimeField(
        'дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class Category(models.Model):
    """Модель для категорий произведений."""

    name = models.CharField(max_length=cr.MAX_NAME_LENGTH, unique=True)
    slug = models.SlugField(max_length=cr.MAX_SLUG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для жанров произведений."""

    name = models.CharField(max_length=cr.MAX_NAME_LENGTH, unique=True)
    slug = models.SlugField(max_length=cr.MAX_SLUG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений (фильмы, книги и т.д.)."""

    name = models.CharField(max_length=cr.MAX_NAME_LENGTH)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles'
    )
    genre = models.ManyToManyField(Genre, related_name='titles')
    reviews = models.ManyToManyField(
        'Review',
        related_name='title_reviews',
        blank=True,
    )

    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class Review(RCBase):
    """Модель для отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews_set',
        verbose_name='произведение',
    )
    score = models.PositiveSmallIntegerField(
        'оценка',
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
        help_text='Оценка от 1 до 10',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            )
        ]

    def __str__(self):
        return f'Отзыв для {self.title.name} от {self.author.username}'


class Comment(RCBase):
    """Модель для комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
