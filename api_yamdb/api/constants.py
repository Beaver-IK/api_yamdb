# =====================================
# Константы отображения для повторяющихся полей
# =====================================
CATEGORY_GENRE_FIELDS = ('name', 'slug')
READ_ONLY_ID = ('id',)
TITLE_FIELDS = (
    'id',
    'name',
    'year',
    'description',
    'category',
    'genre',
    'rating',
)

READ_ONLY_ID_AUTHOR_PUB_DATE = ('id', 'author', 'pub_date')

USER_FIELDS = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
