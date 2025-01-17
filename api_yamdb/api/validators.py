from django.utils.deconstruct import deconstructible
from rest_framework import serializers


@deconstructible
class NotMeValidator:
    """Валидатор для поля username с проверкой на использование 'me'"""

    def __call__(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Нельзя использовать "me" '
                                              'в качестве "username"'
                                              )
