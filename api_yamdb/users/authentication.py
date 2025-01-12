from rest_framework import exceptions
from rest_framework_simplejwt.tokens import AccessToken


def generate_jwt_token(user):
    token = AccessToken.for_user(user)
    return str(token)

def decode_jwt_token(token):
        try:
            payload = AccessToken(token).payload
            return payload
        except Exception as e:
             raise exceptions.AuthenticationFailed(f'Invalid token: {e}')
