import pytz
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import validators

TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=32, choices=TIMEZONE_CHOICES, default="UTC")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Reminder(models.Model):
    header = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    place = models.CharField(max_length=128)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    cc_recipients = models.ManyToManyField(User, related_name="cc_reminders")
    created_at = models.DateTimeField(auto_now_add=True)
    occurs_at = models.DateTimeField(validators=[validators.must_be_future_datetime])


class ReminderTask(models.Model):
    task_id = models.UUIDField(unique=True)
    reminder = models.OneToOneField(Reminder, related_name="task", on_delete=models.CASCADE)
