import pytz
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


def validate_datetime_is_not_past(datetime_):
    if datetime_ < timezone.now():
        raise ValidationError("Must be future date")
    return datetime_

#
# class LocalizedUser(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     timezone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')
#


class Reminder(models.Model):
    header = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    place = models.CharField(max_length=128)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    cc_recipients = models.ManyToManyField(User, related_name="cc_reminders")
    created_at = models.DateTimeField(auto_now_add=True)
    occurs_at = models.DateTimeField(validators=[validate_datetime_is_not_past])  # TODO: validate past dates
