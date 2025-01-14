from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator

from users.models import CustomUser

User = get_user_model()


class Category(models.Model):
    """Модель для категорий произведений."""

    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для жанров произведений."""

    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений (фильмы, книги и т.д.)."""

    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles'
    )
    genre = models.ManyToManyField(Genre, related_name='titles')

    rating = models.FloatField(null=True, default=None)

    def update_average_rating(self):
        """Обновляет средний рейтинг произведения."""
        average = self.reviews.aggregate(models.Avg('score'))['score__avg']
        if average is None:
            self.rating = None
        else:
            self.rating = round(average, 1)
        self.save(update_fields=['rating'])

    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для отзывов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews_set',
    )
    text = models.TextField()
    score = models.PositiveIntegerField(
        validators=[MaxValueValidator(10)],
        help_text='Оценка от 1 до 10',
        null=True,
        blank=True,
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            )
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.title.update_average_rating()

    def __str__(self):
        return f'Отзыв для {self.title.name} от {self.author.username}'


class Comment(models.Model):
    """Модель для комментариев."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )
