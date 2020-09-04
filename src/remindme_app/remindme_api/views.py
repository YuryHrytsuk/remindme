from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from . import models
from . import serializers
from . import tasks


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if "cc" in self.request.query_params:
            queryset = models.Reminder.objects \
                .filter(cc_recipients__id=self.request.user.id) \
                .order_by('occurs_at')
        else:
            queryset = models.Reminder.objects \
                .filter(author=self.request.user) \
                .order_by('occurs_at')
        return queryset

    def perform_create(self, serializer):
        reminder = serializer.save(author=self.request.user)
        tasks.send_reminder.s(reminder.id).apply_async(eta=reminder.occurs_at)


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
