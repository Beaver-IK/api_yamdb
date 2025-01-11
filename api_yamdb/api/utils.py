from django.conf import settings
from django.core.mail import send_mail


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