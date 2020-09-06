from __future__ import absolute_import, unicode_literals

from smtplib import SMTPException

from django.core.mail import send_mail

from remindme_app import celery_app, settings
from . import models


@celery_app.task(bind=True, max_retries=3)
def send_reminder(self, reminder_id):
    reminder = models.Reminder.objects.get(id=reminder_id)
    recipients = [reminder.author.email] + [user.email for user in reminder.cc_recipients.all()]

    try:
        send_mail(
            subject=reminder.header,
            message=reminder.description,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipients
        )
    except SMTPException as e:
        self.retry(exc=e, countdown=2 ** self.request.retries)
    else:
        reminder.delete()
