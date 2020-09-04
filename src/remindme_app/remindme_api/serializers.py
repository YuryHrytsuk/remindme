from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from . import models


class ReminderSerializer(serializers.HyperlinkedModelSerializer):

    def validate_occurs_at(self, value):
        if value < timezone.now():
            raise serializers.ValidationError({
                "occurs_at": "This field can't represent past"
            })
        return value

    class Meta:
        model = models.Reminder
        fields = "__all__"
        read_only_fields = ["author", "created_at"]


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
        fields = ("username", "password", "email")
