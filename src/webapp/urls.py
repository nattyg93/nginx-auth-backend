"""URLs config for whole project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from webapp.views import check_auth

urlpatterns = [
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    path("auth-test/", check_auth, name="auth-test"),
    path("django-admin/", admin.site.urls),
    path(f"{settings.SAML_ROOT_PATH}/", include("djangosaml2.urls")),
]
