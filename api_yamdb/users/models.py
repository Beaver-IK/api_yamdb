from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from users import constants as c


class CustomUserManager(BaseUserManager):
    """кастомный менеджер пользователей."""

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        if not username:
            raise ValueError('Пользователь должен иметь username')
        if not email:
            raise ValueError('Пользователь должен иметь email')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_moderator(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'moderator')
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя."""

    class Roles(models.TextChoices):
        USER = 'user', 'User'
        MODERATOR = 'moderator', 'Moderator'
        ADMIN = 'admin', 'Admin'

    """ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin')
    ]"""

    username = models.CharField(
        max_length=c.MAX_LENGTH_USERNAME,
        unique=True,
        help_text=(
            f'Максимальная длина {c.MAX_LENGTH_USERNAME} символов. ' f'{c.MESSAGE}'
        ),
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=c.MESSAGE,
                code='invalid_username',
            ),
        ],
    )
    email = models.EmailField(max_length=c.EMAIL_LENGTH, unique=True)
    first_name = models.CharField(max_length=c.MAX_LENGTH_FIRST_NAME, blank=True)
    last_name = models.CharField(max_length=c.MAX_LENGTH_LAST_NAME, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.USER)
    confirmation_code = models.CharField(max_length=36, blank=True, null=True)
    validity_code = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        if not self.username:
            raise ValidationError({'username': 'Отсутствует username'})
        if not self.email:
            raise ValidationError({'email': 'Отсутствует email'})

    def generate_code(self):
        import uuid

        self.confirmation_code = str(uuid.uuid4())
        self.validity_code = datetime.now(timezone.utc) + timedelta(hours=24)

    def clear_code(self):
        self.confirmation_code = None
        self.validity_code = None

    @classmethod
    def already_use(cls, kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')
        errors = dict()
        if cls.objects.filter(username=username).exclude(email=email).exists():
            errors['username'] = f'Username {username} уже используется.'
        if cls.objects.filter(email=email).exclude(username=username).exists():
            errors['email'] = f'Email {email} уже используется.'
        return errors

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.Roles.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Roles.MODERATOR
