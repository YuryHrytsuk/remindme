from django.contrib.auth.models import User
from rest_framework import serializers

from . import models
from . import utils


class ReminderSerializer(serializers.HyperlinkedModelSerializer):
    # TODO: exclude self from cc_recipients
    class Meta:
        model = models.Reminder
        fields = "__all__"
        read_only_fields = ["author", "created_at"]
        extra_kwargs = {"cc_recipients": {"allow_empty": True}}


class UserSerializer(serializers.ModelSerializer):
    timezone = serializers.ChoiceField(choices=utils.TIMEZONES, source="profile.timezone", default="UTC")

    def create(self, validated_data):
        print(validated_data)
        user = User(
            email=validated_data["email"],
            username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.save()

        profile = models.Profile(
            user=user,
            timezone=validated_data["timezone"]
        )
        profile.save()

        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("username", instance.email)
        instance.password = validated_data.get("username", instance.password)
        instance.save()

        profile = instance.profile
        profile.timezone = validated_data.get("username", instance.profile.timezone)
        profile.save()

        return instance

    class Meta:
        model = User
        related_fields = ["profile"]
        fields = ["email", "username", "password", "timezone"]
        extra_kwargs = {"password": {"write_only": True}}
