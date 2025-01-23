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

ALLOWED_HOSTS = _filter_empty(os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,0.0.0.0").split(","))


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
    if "dev" in settings.ALLOWED_HOSTS:
        env = RUNTIME_ENVS.DEV
    elif "test" in settings.ALLOWED_HOSTS:
        env = RUNTIME_ENVS.TEST
    elif "prod" in settings.ALLOWED_HOSTS:
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
    "web.core",
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

ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "web.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

STORAGE_DIR = os.environ.get("DJANGO_STORAGE_DIR", BASE_DIR)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(STORAGE_DIR) / os.environ.get("DJANGO_DB_FILE", "django.db"),
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

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
