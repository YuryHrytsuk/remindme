from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from . import serializers
from . import models


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Reminder.objects \
            .filter(author=self.request.user) \
            .order_by('occurs_at')


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
