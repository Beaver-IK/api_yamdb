import jwt
from datetime import timedelta, datetime, timezone
from django.conf import settings
from rest_framework import authentication, exceptions
from users.models import CustomUser


def generate_token(user: CustomUser):
    payload = {
        'id' : user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),
        'iat': datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS384')
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS384'])
        return payload
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Срок действия токена истек!')
    except jwt.InvalidSignatureError:
        raise exceptions.AuthenticationFailed('Недопустимая подпись токена!')
    except jwt.DecodeError:
        raise exceptions.AuthenticationFailed('Недопустимый токен!')
    except Exception as e:
        raise exceptions.AuthenticationFailed(f'Ошибка {e}')


class JWTAuthentication(authentication.BaseAuthentication):
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
                return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix != 'Bearer':
                raise exceptions.AuthenticationFailed('Недопустимый префикс.')
        except ValueError:
            raise exceptions.AuthenticationFailed(
                'Неправильно сформированный заголовок авторизации')

        try:
            payload = decode_token(token)
        except exceptions.AuthenticationFailed:
            raise
        user_id = payload.get('id')
        if not user_id:
            raise exceptions.AuthenticationFailed(
                'В токене отсутсвует id пользователя.')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'Пользователь не найден.'
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                'Пользователь не активен.'
            )
        return (user, token)
