from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class YearValidator(MaxValueValidator):
    """Проверка на корректность года выпуска произведения."""

    message = _('Ensure this value is a correct year.')
    code = 'year_value'

    def __init__(self, message=None):
        super().__init__(lambda: timezone.now().year, message=message)
