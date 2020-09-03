from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Reminder(models.Model):
    header = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    place = models.CharField(max_length=128)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    cc_recipients = models.ManyToManyField(User, related_name="cc_reminders")
    created_at = models.DateTimeField(auto_now_add=True)
    occurs_at = models.DateTimeField()  # TODO: validate past dates
