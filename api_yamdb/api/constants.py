from django.core.validators import RegexValidator
from rest_framework import serializers

from api.validators import NotMeValidator
from users import constants as cu

# =====================================
# Константы для повторяющихся полей
# =====================================
CATEGORY_GENRE_FIELDS = ('id', 'name', 'slug')
READ_ONLY_ID = ('id',)
TITLE_FIELDS = ('id', 'name', 'year', 'description', 'category', 'genre')

READ_ONLY_ID_AUTHOR_PUB_DATE = ('id', 'author', 'pub_date')

USER_FIELDS = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


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
