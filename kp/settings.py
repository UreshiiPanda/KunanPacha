"""
Django settings for kp project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import io
import os

import environ
import google.auth
from google.cloud import secretmanager, storage


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!



# if in Development env
if os.environ.get("KP_PROD", "true") == "false":
    env = environ.Env(DEBUG=False)
    env_file = os.path.join(BASE_DIR, ".env")
    env.read_env(env_file)

    print("App starting in Development Mode")

    DEBUG = True
    SECRET_KEY = env("SECRET_KEY")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env("POSTGRES_NAME"),
            'USER': env("POSTGRES_USER"),
            'PASSWORD': env("POSTGRES_PASSWORD"),
            'HOST': "db",
            'PORT': 5432,
        }
    }


# if in Production env
else:
    print("App starting in Production Mode")


#    SECRET_KEY=(str, os.environ.get("SECRET_KEY"))
#    DATABASE_URL=(str, os.environ.get("DATABASE_URL"))
#    GS_BUCKET_NAME=(str, os.environ.get("GS_BUCKET_NAME"))
#    DEBUG=False
#
#    env = environ.Env(DEBUG=False)
#    env_file = os.path.join(BASE_DIR, ".env")
#    env.read_env(env_file)
#
#    # Attempt to load the Project ID into the environment, safely failing on error.
#    try:
#        _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
#    except google.auth.exceptions.DefaultCredentialsError:
#        pass
#
#    if os.path.isfile(env_file):
#        # Use a local secret file, if provided
#        print("Pulling secrets from local secrets file")
#        env.read_env(env_file)
#    elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
#        # Pull secrets from Secret Manager
#        print("Pulling secrets from GCP Secret Manager")
#        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
#        client = secretmanager.SecretManagerServiceClient()
#        settings_name = os.environ.get("SETTINGS_NAME", "kp-django-settings")
#        name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
#        payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
#        env.read_env(io.StringIO(payload))
#    else:
#        raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")
#
#
#
#


    ###############



    DEBUG = True

    env = environ.Env(
        SECRET_KEY=(str, os.getenv("SECRET_KEY")),
        DATABASE_URL=(str, os.getenv("DATABASE_URL")),
        GS_BUCKET_NAME=(str, os.getenv("GS_BUCKET_NAME")),

    )

    # Attempt to load the Project ID into the environment, safely failing on error.
    try:
        _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        print("google auth error")


    # Use GCP secret manager in prod mode
    if os.getenv("GOOGLE_CLOUD_PROJECT", None):
        print("Pulling secrets from GCP Secret Manager")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        client = secretmanager.SecretManagerServiceClient()
        settings_name = os.getenv("SETTINGS_NAME", "kp-django-settings")
        print(f"settings name: {settings_name}")
        name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
        payload = client.access_secret_version(name=name).payload.data.decode(
            "UTF-8"
        )

        env.read_env(io.StringIO(payload))
        print(f"env {env}")
    else:
        raise Exception(
            "No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found."
        )

    

    print("# # # # # # # # # # # # # # # # # # # # # # # # ## # # # ## # ## #")

    SECRET_KEY = env("SECRET_KEY")
    print("secret_key:", SECRET_KEY)
    DATABASE_URL = env("DATABASE_URL")
    print(f"db_url: {DATABASE_URL}")
    GS_BUCKET_NAME = env("GS_BUCKET_NAME")
    print(f"gs_bucket_name: {GS_BUCKET_NAME}")



    ##############











    # Define static BLOB storage via django-storages[google]
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_DIRS = []
    # IAM creds are being used to access the bucket, so the bucket should not
    # be open for "public reading"
    #GS_DEFAULT_ACL = "publicRead"

    # Use django-environ to parse the connection string
    DATABASES = {"default": env.db()}


ALLOWED_HOSTS = ["*"]


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
]

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"





