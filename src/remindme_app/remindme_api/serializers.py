import celery.result
from django.contrib.auth.models import User
from rest_framework import serializers

from . import models
from . import tasks


class ReminderSerializer(serializers.HyperlinkedModelSerializer):
    def get_fields(self):
        fields = super().get_fields()

        # exclude author of reminder from cc_recipients choices
        current_user = self.context["view"].request.user
        fields["cc_recipients"].child_relation.queryset = User.objects.exclude(id=current_user.id)

        return fields

    def create(self, validated_data):
        instance = super().create(validated_data)

        response = tasks.send_reminder.s(instance.id).apply_async(eta=instance.occurs_at)
        models.ReminderTask.objects.create(task_id=response.task_id, reminder=instance)

        return instance

    def update(self, instance, validated_data):
        """ Celery agnostic update """
        if validated_data["occurs_at"] != instance.occurs_at:
            print(f"Rescheduling celery task for {instance}")
            reminder_task = models.ReminderTask.objects.get(reminder=instance)
            celery_task = celery.result.AsyncResult(reminder_task.task_id)
            celery_task.revoke()

            response = tasks.send_reminder.s(instance.id).apply_async(eta=instance.occurs_at)
            reminder_task.task_id = response.task_id
            reminder_task.save()

        return super().update(instance, validated_data)

    class Meta:
        model = models.Reminder
        fields = "__all__"
        read_only_fields = ["author", "created_at"]
        extra_kwargs = {"cc_recipients": {"allow_empty": True}}


class UserSerializer(serializers.ModelSerializer):
    timezone = serializers.ChoiceField(choices=models.TIMEZONE_CHOICES, source="profile.timezone", default="UTC")

    def create(self, validated_data):
        """ Profile agnostic create """
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
        )
        user.set_password(validated_data["password"])
        user.save()  # create user with default profile

        profile = user.profile
        profile_data = validated_data["profile"]
        profile.timezone = profile_data["timezone"]
        user.save()  # update user profile

        return user

    def update(self, instance, validated_data):
        """ Profile agnostic update """

        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.set_password(validated_data.get("password", instance.password))

        profile = instance.profile
        profile_data = validated_data.get("profile", {})
        profile.timezone = profile_data.get("timezone", instance.profile.timezone)
        instance.save()

        return instance

    class Meta:
        model = User
        fields = ["username", "email", "password", "timezone"]
        related_fields = ["profile"]
        extra_kwargs = {"password": {"write_only": True}}
