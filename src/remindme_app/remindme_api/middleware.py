import pytz
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_anonymous:
            timezone.deactivate()
        else:
            tzname = request.user.profile.timezone
            timezone.activate(pytz.timezone(tzname))

        return self.get_response(request)
