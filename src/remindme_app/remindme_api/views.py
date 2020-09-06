from django.contrib.auth.models import User
from rest_framework import viewsets, permissions as drf_permissions

from . import models
from . import permissions
from . import serializers


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
        serializer.save(author=self.request.user)


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
