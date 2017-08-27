from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_monday(d):
    if d.weekday() != 0:
        raise ValidationError(_("%s is supposed to be a Monday" % d))
