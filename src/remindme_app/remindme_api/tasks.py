from __future__ import absolute_import, unicode_literals

from django.core.mail import send_mail

from remindme_app import celery_app, settings

from . import models


@celery_app.task
def send_reminder(reminder_id):
    reminder = models.Reminder.objects.get(id=reminder_id)
    recipients = [reminder.author.email] + [user.email for user in reminder.cc_recipients.all()]
    send_mail(
        subject=reminder.header,
        message=reminder.description,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipients
    )
    reminder.delete()
