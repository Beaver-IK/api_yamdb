from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_year_not_exceed_current
from reviews import constants as cr

User = get_user_model()


class BaseCategoryGenre(models.Model):
    """Абстрактная модель для моделей Category и Genre."""

    name = models.CharField(
        max_length=cr.MAX_NAME_LENGTH,
        unique=True,
        verbose_name=_("Название"),
        help_text=_("Уникальное название"),
    )
    slug = models.SlugField(
        max_length=cr.MAX_SLUG_LENGTH,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("Уникальная метка"),
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


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


class Category(BaseCategoryGenre):
    """Модель для категорий произведений."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')


class Genre(BaseCategoryGenre):
    """Модель для жанров произведений."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')


class Title(models.Model):
    """Модель для произведений (фильмы, книги и т.д.)."""

    name = models.CharField(
        max_length=cr.MAX_NAME_LENGTH,
        verbose_name=_("Название"),
        db_index=True,
        help_text=_("Название произведения"),
    )
    year = models.SmallIntegerField(
        verbose_name=_("Год выпуска"),
        validators=[validate_year_not_exceed_current],
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name=_("Категория"),
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles', verbose_name=_("Жанры")
    )

    class Meta:
        verbose_name = _("Произведение")
        verbose_name_plural = _("Произведения")
        ordering = ['name']

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
