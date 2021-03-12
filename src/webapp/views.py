"""Webapp views."""
from django.http import HttpResponse


def check_auth(request, *args, **kwargs):  # pylint: disable=unused-argument
    """Return 401 if not authenticated and 204 otherwise."""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    return HttpResponse(status=204)
