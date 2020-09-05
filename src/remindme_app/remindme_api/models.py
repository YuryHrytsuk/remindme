from django.contrib.auth.models import User

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import utils


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=32, choices=utils.TIMEZONES, default="UTC")


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
    cc_recipients = models.ManyToManyField(User, related_name="cc_reminders")  # TODO: check user deletion process
    created_at = models.DateTimeField(auto_now_add=True)
    occurs_at = models.DateTimeField(validators=[utils.validate_datetime_is_not_past])
