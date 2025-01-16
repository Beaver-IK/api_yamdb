from django.conf import settings
from django.core.mail import send_mail
from django.utils.deconstruct import deconstructible
from rest_framework.serializers import ValidationError
from users.models import CustomUser


def send_activation_email(user, request):
        code = user.activation_code
        link = request.build_absolute_uri(f'/api/v1/auth/token/')
        message = (f'Привет {user.username}! \n'
                   f'Отправь на эндпоинт {link} \n'
                   f'username={user.username} и confirmation_code={code}')
        send_mail('Activation',
                     message,
                     settings.EMAIL_HOST_USER,
                    [user.email])


@deconstructible
class NotMeValidator:
        """Валидатор для поля username."""
        def __call__(self, value):
                if value.lower() == 'me':
                        raise ValidationError(
                                'Нельзя использовать "me" '
                                'в качестве "username"')

def already_use(data):
        already_use = CustomUser.already_use(data)
        if already_use:
            raise ValidationError(already_use)
        return data
  