from django.contrib.auth.models import User
from rest_framework import serializers

from . import models
from . import tasks


class ReminderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Reminder
        fields = ("header", "description", "place", "author", "cc_recipients", "created_at", "occurs_at")

    def create(self, *args, **kwargs):
        reminder = super().create(*args, **kwargs)
        tasks.send_reminder.s(reminder.id).apply_async(eta=reminder.occurs_at)
        return reminder


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"]
        )
        user.set_password(validated_data["password"])
        user.save()

        return user

    class Meta:
        model = User
        fields = ("id", "username", "password", "email")
