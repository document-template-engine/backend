"""Настройки проекта."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv("SECRET_KEY_DJANGO", "key does not exist")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "corsheaders",
    "rest_framework",
    "djoser",
    "rest_framework.authtoken",
    "django_filters",
    "api",
    "users",
    "documents",
    "colorfield",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "backend.urls"

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

WSGI_APPLICATION = "backend.wsgi.application"

if os.getenv("BD") == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "django"),
            "USER": os.getenv("POSTGRES_USER", "django"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": int(os.getenv("DB_PORT", "5432")),
        }
    }


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


LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "collected_static"

STATICFILES_DIRS = ((BASE_DIR / "static/"),)

INITIAL_DATA_DIR = BASE_DIR / "data"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 6,
}


DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_ACTIVATION": "optional",
    "PERMISSIONS": {
        "user_list": ["rest_framework.permissions.AllowAny"],
        "user": ["djoser.permissions.CurrentUserOrAdminOrReadOnly"],
    },
    "HIDE_USERS": False,
    "PASSWORD_RESET_CONFIRM_URL": "#/set_password/{uid}/{token}",
    "SERIALIZERS": {
        "user_create": "api.v1.serializers.CustomUserSerializer",
        "user": "api.v1.serializers.CustomUserSerializer",
    },
    "SENDACTIVATIONEMAIL": True,
    "ACTIVATION_URL": "#activation/{uid}/{token}",
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.rambler.ru"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "draftnikox@rambler.ru"
EMAIL_HOST_PASSWORD = "456852Zx"

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Token": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "BASE_PATH": "https://documents-template.site/api/",
}

CORS_ALLOW_ALL_ORIGINS = True  # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOWED_HOSTS = ["localhost"]
