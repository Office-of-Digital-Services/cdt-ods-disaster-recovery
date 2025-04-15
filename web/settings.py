"""
Django settings for Digital Disaster Recovery Center (DDRC) project.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/
"""

import os
from pathlib import Path

from django.conf import settings


def _filter_empty(ls):
    return [s for s in ls if s]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = _filter_empty(os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(","))


class RUNTIME_ENVS:
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


def RUNTIME_ENVIRONMENT():
    """Helper calculates the current runtime environment from ALLOWED_HOSTS."""

    # usage of django.conf.settings.ALLOWED_HOSTS here (rather than the module variable directly)
    # is to ensure dynamic calculation, e.g. for unit tests and elsewhere this setting is needed
    env = RUNTIME_ENVS.LOCAL
    if any(["dev" in host for host in settings.ALLOWED_HOSTS]):
        env = RUNTIME_ENVS.DEV
    elif any(["test" in host for host in settings.ALLOWED_HOSTS]):
        env = RUNTIME_ENVS.TEST
    elif "disasterrecovery.ca.gov" in settings.ALLOWED_HOSTS:
        env = RUNTIME_ENVS.PROD
    return env


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cdt_identity",
    "web.core",
    "web.vital_records",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "web.core.middleware.Healthcheck",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CSRF_COOKIE_AGE = None
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = _filter_empty(os.environ.get("DJANGO_TRUSTED_ORIGINS", "http://localhost").split(","))

# With `Strict`, the user loses their Django session between leaving our app to
# sign in with OAuth, and coming back into our app from the OAuth redirect.
# This is because `Strict` disallows our cookie being sent from an external
# domain and so the session cookie is lost.
#
# `Lax` allows the cookie to travel with the user and be sent back to us by the
# OAuth server, as long as the request is "safe" i.e. GET
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = "_ddrcsessionid"

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

# required so that cross-origin pop-ups have access to parent window context
# see https://github.com/cal-itp/benefits/pull/793
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

# the NGINX reverse proxy sits in front of the application in deployed environments
# SSL terminates before getting to Django, and NGINX adds this header to indicate
# if the original request was secure or not
#
# See https://docs.djangoproject.com/en/5.1/ref/settings/#secure-proxy-ssl-header
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ROOT_URLCONF = "web.urls"

template_ctx_processors = [
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
]

if DEBUG:
    template_ctx_processors.extend(
        [
            "django.template.context_processors.debug",
        ]
    )

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": template_ctx_processors,
        },
    },
]

WSGI_APPLICATION = "web.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DJANGO_DB_NAME", "django"),
        "USER": os.environ.get("DJANGO_DB_USER", "django"),
        "PASSWORD": os.environ.get("DJANGO_DB_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOSTNAME", "postgres"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "web", "static")]
# use Manifest Static Files Storage by default
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": os.environ.get(
            "DJANGO_STATICFILES_STORAGE", "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        )
    },
}
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "WARNING")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname} {name}:{lineno} {message}",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
