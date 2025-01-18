from django.core.validators import RegexValidator
from rest_framework import serializers

from api.validators import NotMeValidator
from users import constants as cu


# =====================================
# Поле USERNAME_FIELD
# =====================================
USERNAME_FIELD = serializers.CharField(
    max_length=cu.MAX_LENGTH_USERNAME,
    validators=[
        RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=cu.MESSAGE,
            code='invalid_username',
        ),
        NotMeValidator(),
    ],
)
