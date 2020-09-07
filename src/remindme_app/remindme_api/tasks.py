import logging
import socket
from smtplib import SMTPException

import celery.exceptions
from django.core.mail import send_mail

from remindme_app import celery_app, settings
from . import models

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_notification(self, reminder_id):
    reminder = models.Reminder.objects.get(id=reminder_id)
    recipients = [reminder.author.email] + [user.email for user in reminder.cc_recipients.all()]

    try:
        send_mail(
            subject=reminder.header,
            message=reminder.description,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipients
        )
    except (SMTPException, ConnectionError, socket.gaierror) as e:
        try:
            self.retry(countdown=2 ** self.request.retries)
        except celery.exceptions.MaxRetriesExceededError:
            logger.warning(f"Failed to send notification for {reminder=}")
            raise
    else:
        reminder.delete()
