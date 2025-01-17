from rest_framework_simplejwt.tokens import AccessToken


def generate_jwt_token(user):
    token = AccessToken.for_user(user)
    return str(token)
