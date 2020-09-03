from __future__ import absolute_import, unicode_literals

from remindme_app import celery_app

from . import models


@celery_app.task
def show_reminders():
    return [m.id for m in models.Reminder.objects.all()]
