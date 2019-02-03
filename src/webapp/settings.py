"""Settings for your application."""

from typing import List, Tuple

from configurations import values  # type: ignore
from ionata_settings import base


class Project:
    """Settings unique to your project's base Configuration."""

    APP_NAME = "webapp"

    SITE_URL = values.Value(environ_required=True)

    AUTH_USER_MODEL = "auth.User"

    # Storage
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

    # Auth
    SESSION_COOKIE_PATH = "/"
    CSRF_COOKIE_PATH = "/"

    @property
    def INSTALLED_APPS(self):  # pylint: disable=invalid-name
        """Add additional installed apps."""
        apps_to_remove = [
            "minimal_user",
            "anymail",
            "storages",
            "django_celery_beat",
            "django_celery_results",
        ]
        return ["webapp"] + [
            app for app in super().INSTALLED_APPS if app not in apps_to_remove
        ]

    @property
    def EMAIL_SUBJECT_PREFIX(self):
        """Override email subject prefix."""
        return "[Django - Nginx Auth Backend] "


class Dev(Project, base.Dev):
    """Override development settings."""


class Prod(Project, base.Prod):
    """Override production settings."""

    ADMINS = [("Webmaster", "webmaster@ionata.com.au")]
    MANAGERS = [("Webmaster", "webmaster@ionata.com.au")]
    ALLOWED_HOSTS: List[str] = values.ListValue(environ_required=True)
