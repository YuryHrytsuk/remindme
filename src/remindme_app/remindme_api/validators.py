from django.core.exceptions import ValidationError
from django.utils import timezone


def must_be_future_datetime(datetime_):
    if datetime_ < timezone.now():
        raise ValidationError("Must be future date")
    return datetime_
