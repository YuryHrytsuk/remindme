from django.contrib.auth.models import User
from rest_framework import viewsets, permissions as drf_permissions

from . import models
from . import permissions
from . import serializers
from . import tasks


class ReminderViewSet(viewsets.ModelViewSet):
    model = models.Reminder
    queryset = models.Reminder.objects.all()
    serializer_class = serializers.ReminderSerializer

    def get_queryset(self):
        if "cc" in self.request.query_params:
            queryset = self.queryset.filter(cc_recipients__id=self.request.user.id)
        else:
            queryset = self.queryset.filter(author=self.request.user)

        queryset = queryset.order_by('occurs_at')
        return queryset

    def perform_create(self, serializer):
        reminder = serializer.save(author=self.request.user)
        tasks.send_reminder.s(reminder.id).apply_async(eta=reminder.occurs_at)


class UserView(viewsets.ModelViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [drf_permissions.IsAuthenticated, drf_permissions.IsAdminUser]
        elif self.action == "create":
            permission_classes = [drf_permissions.AllowAny]
        else:
            permission_classes = [drf_permissions.IsAuthenticated, permissions.IsSelfOrAdminUser]

        return [pc() for pc in permission_classes]
