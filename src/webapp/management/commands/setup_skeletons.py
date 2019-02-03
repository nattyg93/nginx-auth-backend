"""Automatically populate information in the database."""
from functools import reduce
from operator import or_

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.utils import IntegrityError

from users import models


def populate_default_groups() -> None:
    """Ensure relevant Groups exist and have correct Permissions."""
    for group_info in settings.AUTH_GROUPS:
        group = Group.objects.get_or_create(name=group_info["name"])[0]
        perm_q_list = []
        for perm in group_info["permissions"]:
            app_label, codename = perm.split(".")
            perm_q_list.append(Q(content_type__app_label=app_label, codename=codename))
        perm_q = reduce(or_, (perm_q_list))
        group.permissions.set(Permission.objects.filter(perm_q))


def get_admin() -> models.User:
    """Return the default admin, creating it if not present."""
    admin = settings.ADMIN_USER
    username = models.User.USERNAME_FIELD
    restrict = [username, "password"]
    defaults = {x: True for x in ["is_staff", "is_superuser", "is_active"]}
    env_vals = {k: v for k, v in admin.items() if k not in restrict}
    defaults.update(env_vals)
    try:
        values = {username: admin[username], "defaults": defaults}
        user, new = models.User.objects.get_or_create(**values)
    except IntegrityError:
        raise AttributeError("Admin user not found or able to be created.")
    if new:
        user.set_password(admin["password"])
        user.save()
    return user


def get_site() -> Site:
    """Return the default site, creating it if not present."""
    defaults = {"name": settings.APP_NAME, "domain": settings.URL.hostname}
    kwargs = {"pk": settings.SITE_ID, "defaults": defaults}
    return Site.objects.get_or_create(**kwargs)[0]


def ensure_all_users_have_profiles():
    """Create a Profile for ever User that does not have one."""
    profiles = []
    for user in models.User.objects.filter(profile__isnull=True).distinct():
        profiles.append(models.Profile(user=user))
    models.Profile.objects.bulk_create(profiles)


class Command(BaseCommand):
    """Management Command to run the setup_skeletons actions."""

    def handle(self, *args, **options) -> None:
        """Run the necessary apps."""
        print(f"Running setup for {settings.APP_NAME}")
        populate_default_groups()
        get_admin()
        get_site()
        ensure_all_users_have_profiles()
