"""URLs config for whole project."""
from typing import Any, List

from django.conf import settings
from django.contrib.auth.views import LoginView, logout_then_login
from django.urls import include, path

from webapp.views import check_auth


def _static_urls() -> List[Any]:
    if not settings.DEBUG:
        return []
    from django.conf.urls.static import static
    from django.contrib.staticfiles import urls

    _static = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    return urls.staticfiles_urlpatterns() + _static


urlpatterns = [
    path("auth-login/", LoginView.as_view(), name="login"),
    path("auth-test/", check_auth, name="auth-test"),
    path("auth-logout/", logout_then_login, name="logout"),
    path("", include(_static_urls())),
]
