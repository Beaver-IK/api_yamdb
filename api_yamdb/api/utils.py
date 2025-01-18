from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.deconstruct import deconstructible
from rest_framework.serializers import ValidationError

User = get_user_model()


def send_activation_email(user):
    """Функция отправки письма."""
    code = user.confirmation_code
    message = (f'Привет {user.username}! \n'
               f'Confirmation_code:{code}')
    send_mail('Activation',
              message,
              settings.EMAIL_HOST_USER,
              [user.email])


def build_filter_for_title(query_params):
    """Формирует словарь фильтров для модели Title."""
    param_map = dict(
        category='category__slug',
        genre='genre__slug',
        year='year',
        name='name__icontains'
    )
    filters_dict = dict()
    for query_param, filter_field in param_map.items():
        value = query_params.get(query_param)
        if value:
            filters_dict[filter_field] = value
    return filters_dict


def already_use(data):
    """Функция проверки занятости username и email."""
    already_use = User.already_use(data)
    if already_use:
        raise ValidationError(already_use)
    return data


def validate_year_not_exceed_current(value: int) -> int:
    """Проверяет, что год не превышает текущий год."""
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(
            'Год выпуска произведения не может '
            f'превышать текущий год ({current_year}).'
        )
    return value


def validate_not_empty(value, field_name: str = 'поле') -> None:
    """Проверяет, что переданное значение не пустое."""
    if not value:
        raise ValidationError(
            f'Список {field_name} ' 'не может быть пустым.'
        )
    return value


def update_instance_fields(instance, validated_data: dict):
    """Обновляет поля объекта на основе validated_data и сохраняет."""
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance
