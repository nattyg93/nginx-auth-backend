"""Management Command to setup initial data."""
from enum import Enum
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


def get_admin():
    """Return the default admin, creating it if not present."""
    admin = settings.ADMIN_USER
    model = get_user_model()
    if model is None:
        raise ImportError("Cannot import the specified User model")
    username = model.USERNAME_FIELD
    restrict = [username, "password"]
    defaults = {x: True for x in ["is_staff", "is_superuser", "is_active"]}
    env_vals = {k: v for k, v in admin.items() if k not in restrict}
    defaults.update(env_vals)
    try:
        values = {username: admin[username], "defaults": defaults}
        user, new = model.objects.get_or_create(**values)
    except IntegrityError as error:
        raise AttributeError("Admin user not found or able to be created.") from error
    if new:
        user.set_password(admin["password"])
        user.save()
    return user


def get_site():
    """Return the default site, creating it if not present."""
    url = urlparse(settings.SITE_URL)
    defaults = {"name": settings.PROJECT_NAME, "domain": url.hostname}
    kwargs = {"pk": settings.SITE_ID, "defaults": defaults}
    return Site.objects.get_or_create(**kwargs)[0]


class Verbosity(Enum):
    """Verbosity enum."""

    MINIMAL = 0
    NORMAL = 1
    VERBOSE = 2
    VERY_VERBOSE = 3

    def __ge__(self, other):
        """Return true if this instance is greater than or equal to other."""
        if self.__class__ is other.__class__:
            return self.value >= other.value  # pylint: disable=comparison-with-callable
        return NotImplemented

    def __gt__(self, other):
        """Return true if this instance is greater than other."""
        if self.__class__ is other.__class__:
            return self.value > other.value  # pylint: disable=comparison-with-callable
        return NotImplemented

    def __le__(self, other):
        """Return true if this instance is less than or equal to other."""
        if self.__class__ is other.__class__:
            return self.value <= other.value  # pylint: disable=comparison-with-callable
        return NotImplemented

    def __lt__(self, other):
        """Return true if this instance is less than other."""
        if self.__class__ is other.__class__:
            return self.value < other.value  # pylint: disable=comparison-with-callable
        return NotImplemented


class Command(BaseCommand):
    """Management command to setup initial data."""

    def __init__(self, *args, **kwargs):
        """Set default verbosity."""
        super().__init__(*args, **kwargs)
        self.verbosity: Verbosity

    def _log(self, message, level=Verbosity.NORMAL, style=None):
        if self.verbosity >= level:
            output = message
            if style is not None:
                output = style(message)
            self.stdout.write(output)

    def handle(self, *args, **options):
        """Run the management command."""
        self.verbosity = Verbosity(options["verbosity"])
        self._log(f"Running setup for {settings.PROJECT_NAME}", style=self.style.NOTICE)
        get_admin()
        get_site()
