"""URLs config for whole project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, logout_then_login
from django.urls import path

from webapp.views import check_auth

urlpatterns = [
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    path("auth-login/", LoginView.as_view(), name="login"),
    path("auth-test/", check_auth, name="auth-test"),
    path("auth-logout/", logout_then_login, name="logout"),
    path("django-admin/", admin.site.urls),
]
