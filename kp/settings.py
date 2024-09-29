"""
Django settings for kp project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import io
import json
import logging
import os
import socket
from pathlib import Path

import environ
import google.auth
from google.cloud import secretmanager
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# if in Development env
if os.environ.get("KP_PROD", "true") == "false":
    env = environ.Env(DEBUG=False)
    env_file = os.path.join(BASE_DIR, ".env")
    env.read_env(env_file)

    print("App starting in Development Mode")
    print(
        f"postgres details: name: {env('POSTGRES_NAME')}, user: {env('POSTGRES_USER')}, pass: {env('POSTGRES_PASSWORD')}"
    )

    ALLOWED_HOSTS = ["*"]

    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    DEBUG = True
    SECRET_KEY = env("SECRET_KEY")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_NAME"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": "db",
            "PORT": 5432,
        }
    }

    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

    # Add this after your DATABASES configuration
    db_host = DATABASES["default"]["HOST"]
    try:
        db_ip = socket.gethostbyname(db_host)
        print(f"Database host '{db_host}' resolves to IP: {db_ip}")
    except socket.gaierror:
        print(f"Could not resolve host: {db_host}")

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "kp_app", "static"),
    ]


# if in Production env
else:
    print("App starting in Production Mode")

    DEBUG = False

    # Allow CSRF to work in Prod
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "kp-run-pdjzxrqjaq-uc.a.run.app"]
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "https://kp-run-pdjzxrqjaq-uc.a.run.app",
    ]
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

    env = environ.Env(
        SECRET_KEY=(str, os.getenv("SECRET_KEY")),
        DATABASE_URL=(str, os.getenv("DATABASE_URL")),
        GS_BUCKET_NAME=(str, os.getenv("GS_BUCKET_NAME")),
        EMAIL_HOST_USER=(str, os.getenv("EMAIL_HOST_USER")),
        EMAIL_HOST_PASSWORD=(str, os.getenv("EMAIL_HOST_PASSWORD")),
    )
    print(
        "SECRET_KEY, DATABASE_URL, GS_BUCKET_NAME, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD have been pulled from GCP into the Django app"
    )

    # Attempt to load the Project ID into the environment, safely failing on error.
    try:
        _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
        print("google auth successful")
    except google.auth.exceptions.DefaultCredentialsError:
        print("google auth error")

    # Use GCP secret manager in prod mode
    if os.getenv("GOOGLE_CLOUD_PROJECT", None):
        print("Django app is Pulling secrets from GCP Secret Manager")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        client = secretmanager.SecretManagerServiceClient()
        settings_name = os.getenv("SETTINGS_NAME", "kp-django-settings")
        name = f"projects/{project_id}/secrets/{settings_name}/versions/1"
        payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

        env.read_env(io.StringIO(payload))
    else:
        raise Exception(
            "No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found."
        )

    SECRET_KEY = env("SECRET_KEY")
    DATABASE_URL = env("DATABASE_URL")
    GS_BUCKET_NAME = env("GS_BUCKET_NAME")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

    GCP_SERVICE_ACCOUNT_KEY = env("GCP_SERVICE_ACCOUNT_KEY")
    if GCP_SERVICE_ACCOUNT_KEY:
        print("GCP_SERVICE_ACCOUNT_KEY: ", GCP_SERVICE_ACCOUNT_KEY)
        GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
            json.loads(GCP_SERVICE_ACCOUNT_KEY)
        )
        print("GCP_SERVICE_ACCOUNT_KEY found in environment variables")
    else:
        # Handle the case where the key is not available
        print("WARNING - GCP_SERVICE_ACCOUNT_KEY not found in environment variables")
        GS_CREDENTIALS = None

    # Define static BLOB storage via django-storages[google]
    # so django-storages is being used here to interface with Google Cloud instead of
    # using the google.cloud import directly
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_DIRS = []
    STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
    # bucket must be set to allow ACLs and it must not prevent public access
    # GS_DEFAULT_ACL = "publicRead"

    # media route for SummerNote
    MEDIA_URL = "/media/"
    MEDIA_ROOT = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

    if os.environ.get("USE_CLOUD_SQL_AUTH_PROXY") == "true":
        # Prod DB when needing to run make-migrations
        # Use django-environ to parse the connection string

        env = environ.Env(DEBUG=False)
        env_file = os.path.join(BASE_DIR, ".env")
        env.read_env(env_file)

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "HOST": "127.0.0.1",
                "PORT": "5432",
                "NAME": env("PROXY_DB_NAME"),
                "USER": env("PROXY_DB_USER"),
                "PASSWORD": env("PROXY_DB_PASSWORD"),
            }
        }

    else:
        # Prod DB (without make-migrations)
        # Use django-environ to parse the connection string
        DATABASES = {"default": env.db()}


# Application definitions
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "kp_app",
    "widget_tweaks",
    "django_summernote",
]


AUTH_USER_MODEL = "auth.User"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kp.urls"

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

WSGI_APPLICATION = "kp.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
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


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # End session when browser closes

# end a session automatically after 12 hours
SESSION_COOKIE_AGE = 43200  # in seconds (e.g., 12 hour)


SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
