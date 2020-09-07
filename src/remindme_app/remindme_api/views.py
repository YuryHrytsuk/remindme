import celery.result
from django.contrib.auth.models import User
from django.utils import timezone, dateparse
from rest_framework import viewsets, permissions as drf_permissions
from rest_framework.exceptions import ValidationError

from . import models
from . import permissions
from . import serializers
from . import tasks


class ReminderViewSet(viewsets.ModelViewSet):
    model = models.Reminder
    serializer_class = serializers.ReminderSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        if "cc" in self.request.query_params:
            queryset = models.Reminder.objects.filter(cc_recipients__id=self.request.user.id)
        else:
            queryset = models.Reminder.objects.filter(author=self.request.user)

        queryset = queryset.order_by('occurs_at')
        return queryset

    def perform_create(self, serializer):
        """ Notification agnostic create """
        reminder = serializer.save(author=self.request.user)
        response = tasks.send_notification.s(reminder.id).apply_async(eta=reminder.occurs_at)
        reminder_task = models.ReminderTask(task_id=response.task_id, reminder=reminder)
        reminder_task.save()

    def perform_update(self, serializer):
        """ Notification agnostic update """
        if "occurs_at" not in serializer.initial_data:  # no update for occurs_at - skipping
            return super().perform_update(serializer)

        occurs_at = dateparse.parse_datetime(serializer.initial_data["occurs_at"])
        if timezone.is_naive(occurs_at):
            occurs_at = timezone.make_aware(occurs_at)
        reminder = self.get_object()

        if occurs_at == reminder.occurs_at:  # new occurs_at is equal to old value - skipping
            return super().perform_update(serializer)

        celery_task = celery.result.AsyncResult(reminder.task.task_id)

        if celery_task.status != "PENDING":  # celery task has been launched - we cannot revoke it safely now
            raise ValidationError({"occurs_at": "Cannot revoke notification. It has been launched by now"})

        celery_task.revoke()  # revoke old task

        response = tasks.send_notification.s(reminder.id).apply_async(eta=occurs_at)  # schedule task with update eta
        reminder.task.task_id = response.task_id
        reminder.task.save()

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        """ Celery agnostic destroy """
        celery_task = celery.result.AsyncResult(instance.task.task_id)
        celery_task.revoke()  # we do our best here
        return super().perform_destroy(instance)


class UserView(viewsets.ModelViewSet):
    model = User
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        """ Manually handling permission for list action """

        if self.action != "list":
            return User.objects.all()

        if self.request.user.is_staff:
            queryset = User.objects.all()
        elif self.request.user.is_anonymous:
            queryset = User.objects.none()
        else:
            queryset = User.objects.filter(id=self.request.user.id)

        return queryset

    def get_permissions(self):
        if self.action == "list":
            # AllowAny to have a sign up form. We limit user access by `get_queryset`
            permission_classes = [drf_permissions.AllowAny]
        elif self.action == "create":
            permission_classes = [drf_permissions.AllowAny]
        else:
            permission_classes = [drf_permissions.IsAuthenticated, permissions.IsSelfOrAdminUser]

        return [pc() for pc in permission_classes]
