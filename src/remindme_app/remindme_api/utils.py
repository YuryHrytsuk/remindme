import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


def validate_datetime_is_not_past(datetime_):
    if datetime_ < timezone.now():
        raise ValidationError("Must be future date")
    return datetime_
