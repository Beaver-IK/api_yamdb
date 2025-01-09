from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

MAX_LENGTH = 150
MESSAGE = (f'Возможно испошльзование букв, цифр и спецсимволов @,.,+,-,_')
EMAIL_LENGTH = 254


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(username, email, password, **extra_fields)

class CastomUser(AbstractBaseUser):
    """Кастомная модель пользователя."""
    
    ROLE_CHOICES = [
      ('user', 'User'),
      ('moderator', 'Moderator'),
      ('admin', 'Admin')
    ]
    
    user_id = models.BigAutoField(primary_key=True, editable=False)
    username = models.CharField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text=f'Максимальная длина {MAX_LENGTH} символов. {MESSAGE}',
        validators= [
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=MESSAGE,
                code='invalid_username',   
            ),
        ],
    )
    email = models.EmailField(max_length=EMAIL_LENGTH, unique=True)
    first_name = models.CharField(max_length=MAX_LENGTH, blank=True)
    last_name = models.CharField(max_length=MAX_LENGTH, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


    def __str__(self):
        return self.username

    def clean(self):
         super().clean()
         if not self.username:
            raise ValidationError({'username': 'Username is required.'})
         if not self.email:
            raise ValidationError({'email': 'Email is required.'})
