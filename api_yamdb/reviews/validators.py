import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_year_not_exceed_current(year):
    """Валидатор, запрещающий указать год больше текущего."""
    current_year = datetime.date.today().year
    if year > current_year:
        raise ValidationError(
            _('Год %(year)s должен быть меньше текущего (%(current_year)s).'),
            params={'year': year, 'current_year': current_year},
        )
