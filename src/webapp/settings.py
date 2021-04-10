"""Settings for your application."""
import os.path
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type
from urllib.parse import urlparse

import saml2
import saml2.saml
from environ import Env

env = Env()

# Bootstrap debug
DEBUG = env.bool("DEBUG")

default_databse_url = env.NOTSET

scheme: Dict[str, Tuple[Type, Any]] = {
    "CELERY_BROKER_URL": (str, "redis://"),
    "AXES_META_PRECEDENCE_ORDER": (tuple, ("HTTP_X_FORWARDED_FOR", "X_FORWARDED_FOR")),
}

if DEBUG:
    default_databse_url = (  # pylint: disable=invalid-name
        "postgres://django:django@db:5432/django"
    )
    scheme = {
        **scheme,
        **{
            "CELERY_BROKER_URL": (str, "redis://redis/0"),
            "ADMIN_USER": (dict, {"email": "test@example.com", "password": "password"}),
            "MAILGUN_API_KEY": (str, ""),
            "CELERY_TASK_DEFAULT_QUEUE": (str, "celery"),
            "AXES_KEY_PREFIX": (str, "axes"),
            "AXES_REDIS_URL": (str, "rediscache://redis/1"),
            "SECRET_KEY": (str, "super_secret_secret_key"),
        },
    }

env = Env(**scheme)

# Core
PROJECT_NAME: str = "nginx_auth_backend"
SECRET_KEY: str = env("SECRET_KEY")
SITE_URL: str = env("SITE_URL")
# NOTE: We do not use the axes middleware because we want login attempts to
# silently fail. Thus we silence `axes.W002` (invalid MIDDLEWARE configuration).
SILENCED_SYSTEM_CHECKS = ["axes.W002"]

url = urlparse(SITE_URL)

ADMINS: List[Tuple[str, str]] = [("webmaster", "webmaster@ionata.com.au")]
MANAGERS = ADMINS
ADMIN_USER = env.dict("ADMIN_USER")
ALLOWED_HOSTS: List[str] = [".nattyg93.com"]
CORS_ORIGIN_WHITELIST: List[str] = [SITE_URL]


# Services
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# NOTE: This needs to be set to something unique per site so that the different
# celery instances data is namespaced on the shared broker (probably redis)
CELERY_TASK_DEFAULT_QUEUE = env.str("CELERY_TASK_DEFAULT_QUEUE")
DATABASES = {"default": env.db_url(default=default_databse_url)}

# Storage
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

INSTALLED_APPS = [
    # Project apps
    "webapp.apps.WebAppConfig",
    # 3rd party
    "djangosaml2",
    # Our defaults
    "corsheaders",
    "django_extensions",
    "django_celery_beat",
    "django_celery_results",
    # Core django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "axes",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "djangosaml2.middleware.SamlSessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

ROOT_URLCONF = "webapp.urls"
WSGI_APPLICATION = "webapp.wsgi.application"
SITE_ID = 1

# i18n
LANGUAGE_CODE = "en-AU"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Auth
ANONYMOUS_USER_ID = -1
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
    "djangosaml2.backends.Saml2Backend",
]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "saml2_login"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# SAML
SAML_ROOT_PATH = "saml"
SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_POST
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_POST
SAML_IGNORE_LOGOUT_ERRORS = True
IDP_URL = env("IDP_URL")
IDP_METADATA_PATH = env(
    "IDP_METADATA_PATH", default="/auth/realms/master/protocol/saml/descriptor"
)
SAML_DJANGO_USER_MAIN_ATTRIBUTE = "username"
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = "__iexact"
SAML_ATTRIBUTE_MAPPING = {
    "username": ("username",),
    "mail": ("email",),
    "cn": ("first_name",),
    "sn": ("last_name",),
}
ACS_DEFAULT_REDIRECT_URL = "/"

SAML_DIR = env("SAML_DIR")

SAML_CONFIG = {
    "xmlsec_binary": "/usr/bin/xmlsec1",
    "entityid": f"{SITE_URL}/{SAML_ROOT_PATH}/metadata/",
    "attribute_map_dir": os.path.join(SAML_DIR, "attribute_maps"),
    "service": {
        "sp": {
            "name": "Service Gateway",
            "name_id_format": saml2.saml.NAMEID_FORMAT_PERSISTENT,
            "endpoints": {
                "assertion_consumer_service": [
                    (f"{SITE_URL}/{SAML_ROOT_PATH}/acs/", saml2.BINDING_HTTP_POST),
                ],
                "single_logout_service": [
                    (f"{SITE_URL}/{SAML_ROOT_PATH}/ls/post/", saml2.BINDING_HTTP_POST),
                ],
            },
            "force_authn": False,
            "authn_requests_signed": True,
            "name_id_format_allow_create": False,
            "allow_unsolicited": True,
            "required_attributes": ["uid", "username"],
            "optional_attributes": ["eduPersonAffiliation"],
        },
    },
    "metadata": {
        "remote": [
            {
                "url": f"{IDP_URL}{IDP_METADATA_PATH}",
                "disable_ssl_certificate_validation": False,
            },
        ],
    },
    "debug": 0,
    "key_file": os.path.join(SAML_DIR, "private.key"),
    "cert_file": os.path.join(SAML_DIR, "public.pem"),
    # own metadata settings
    "contact_person": [
        {
            "given_name": "Nat",
            "sur_name": "Gordon",
            "company": "NattyG93",
            "email_address": "webmaster@nattyg93.com",
            "contact_type": "technical",
        },
    ],
    # you can set multilanguage information here
    "organization": {
        "name": [("NattyG93", "en")],
        "display_name": [("NattyG93", "en")],
        "url": [("https://nattyg93.com", "en")],
    },
}


# Security
INTERNAL_IPS = ["127.0.0.1"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Files
project_root = Path(__file__).parents[2]
MEDIA_ROOT = f"{project_root}/var/media/assets/media/"
STATIC_ROOT = f"{project_root}/var/media/assets/static/"
MEDIA_URL = "/assets/media/"
STATIC_URL = "/assets/static/"


# Celery
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}  # 1 hour.
CELERY_RESULT_BACKEND = "django-db"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_APP_NAME = PROJECT_NAME

# Email
EMAIL_SUBJECT_PREFIX = f"[Django - {PROJECT_NAME}] "
DEFAULT_FROM_EMAIL = f"no-reply@{url.hostname}"
SERVER_EMAIL = f"no-reply@{url.hostname}"

# Misc
FRONTEND_URL = SITE_URL

# Django-axes
AXES_HANDLER = "axes.handlers.cache.AxesCacheHandler"
AXES_CACHE = "axes"
AXES_ENABLE_ADMIN = False
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = timedelta(hours=1)
# NOTE: This value should be set in the env to use HTTP_X_FORWARDED_FOR in most
# cases since most projects will be behind a reverse proxy.
# WARNING: *DO NOT* put HTTP_X_FORWARDED_FOR in the variable if this project is
# not hosted behind a reverse proxy, as the HTTP_X_FORWARDED_FOR header can
# be spoofed.
env_axes_meta_precedence_order = env("AXES_META_PRECEDENCE_ORDER")
if env_axes_meta_precedence_order is not None:
    AXES_META_PRECEDENCE_ORDER = env_axes_meta_precedence_order
    remote_addr = "REMOTE_ADDR"  # pylint: disable=invalid-name
    if remote_addr not in AXES_META_PRECEDENCE_ORDER:
        AXES_META_PRECEDENCE_ORDER += (remote_addr,)


# Caches
axes_cache_config: Dict[str, Any] = {"OPTIONS": {}, **env.cache_url("AXES_REDIS_URL")}
# NOTE: This needs to be set to something unique per site so that the different
# instances django-axes data is namespaced in the shared cache (probably redis)
axes_cache_config["KEY_PREFIX"] = env("AXES_KEY_PREFIX")
axes_cache_config["OPTIONS"][
    "SERIALIZER"
] = "django_redis.serializers.json.JSONSerializer"
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    AXES_CACHE: axes_cache_config,
}

# DRF Core
INSTALLED_APPS += [
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "allauth",
    "django_filters",
]
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "EXCEPTION_HANDLER": "rest_framework_json_api.exceptions.exception_handler",
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework_json_api.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework_json_api.renderers.JSONRenderer"],
    "DEFAULT_METADATA_CLASS": "rest_framework_json_api.metadata.JSONAPIMetadata",
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework_json_api.filters.QueryParameterValidationFilter",
        "rest_framework_json_api.filters.OrderingFilter",
        "rest_framework_json_api.django_filters.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    "SEARCH_PARAM": "filter[search]",
    "DEFAULT_PAGINATION_CLASS": "webapp.pagination.JsonApiPageNumberPagination",
    "PAGE_SIZE": 100,
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework_json_api.renderers.JSONRenderer",
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "vnd.api+json",
}

# DRF Auth
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
REST_AUTH_SERIALIZERS = {
    "PASSWORD_RESET_SERIALIZER": "users.serializers.PasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "users.serializers.PasswordResetConfirmSerializer",
    "LOGIN_SERIALIZER": "users.serializers.LoginSerializer",
    "TOKEN_SERIALIZER": "users.serializers.TokenSerializer",
}

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    ADMINS = [("Nat Gordon", "nat@nattyg93.com")]
    MANAGERS = ADMINS

    # Security
    CORS_ORIGIN_ALLOW_ALL = True
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Email
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # CORS
    CORS_ORIGIN_WHITELIST = [item for item in ALLOWED_HOSTS if item != "*"]

# Post debug setup dependant settings
CSRF_TRUSTED_ORIGINS = [urlparse(origin).netloc for origin in CORS_ORIGIN_WHITELIST]
