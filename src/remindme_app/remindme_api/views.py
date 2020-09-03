from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from . import models
from . import serializers


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_reminders_by_author()

    def get_reminders_by_author(self):
        return models.Reminder.objects \
            .filter(author=self.request.user) \
            .order_by('occurs_at')

    def get_reminders_including_author(self):
        return models.Reminder.objects \
            .filter(cc_recipients__id=self.request.user.id) \
            .order_by('occurs_at')

    def list(self, request, *args, **kwargs):
        if "cc" in request.query_params:
            with patch.object(self, "get_queryset", self.get_reminders_including_author):
                result = super().list(request, *args, **kwargs)

        else:
            result = super().list(request, *args, **kwargs)

        return result


class CreateUserView(viewsets.ModelViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [p() for p in permission_classes]
