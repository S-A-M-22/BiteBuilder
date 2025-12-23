"""
Django settings for BiteBuilderApp project
Production-optimized for EC2 with HTTPS (Nginx + uWSGI + React frontend).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ==============================
# CORE CONFIG
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(override=True)

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SERVER_IP = os.getenv("SERVER_IP", "54.226.22.0")
SECRET_KEY = os.getenv("SECRET_KEY")

# Crash early if secrets missing
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables.")

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [
        SERVER_IP,
        "bitebuilder.duckdns.org",
        "localhost",
        "127.0.0.1",
    ]

# ==============================
# APPLICATIONS
# ==============================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.users",
    "apps.api",
    "rest_framework",
    "corsheaders",
]
INSTALLED_APPS += ["django_prometheus"]


# ==============================
# MIDDLEWARE
# ==============================
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",   # ⬅️ add here (first)
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.api.middleware.EnforceOtpMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",    # ⬅️ add here (last)
]


ROOT_URLCONF = "BiteBuilderApp.urls"
WSGI_APPLICATION = "BiteBuilderApp.wsgi.application"

# ==============================
# TEMPLATES
# ==============================
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

# ==============================
# DATABASE
# ==============================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ==============================
# STATIC FILES
# ==============================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==============================
# SECURITY SETTINGS
# ==============================
if DEBUG:
    # Development: relaxed SSL for localhost + Vite
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0

    # Local trust (Vite on HTTPS)
    CSRF_TRUSTED_ORIGINS = [
        "https://localhost:5173",
        "https://127.0.0.1:8000",
    ]
    CORS_ALLOWED_ORIGINS = [
        "https://localhost:5173",
    ]
else:
    # Production: full HTTPS hardening
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    CSRF_TRUSTED_ORIGINS = [
        "https://bitebuilder.duckdns.org",
        f"https://{SERVER_IP}",
    ]
    CORS_ALLOWED_ORIGINS = [
        "https://bitebuilder.duckdns.org",
        f"https://{SERVER_IP}",
    ]

SECURE_REFERRER_POLICY = "strict-origin"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

CORS_ALLOW_CREDENTIALS = True

# ==============================
# FATSECRET / API KEYS
# ==============================
FATSECRET_CONSUMER_KEY = os.getenv("FATSECRET_CONSUMER_KEY")
FATSECRET_CONSUMER_SECRET = os.getenv("FATSECRET_CONSUMER_SECRET")
FATSECRET2_CLIENT_ID = os.getenv("FATSECRET2_CLIENT_ID")
FATSECRET2_CLIENT_SECRET = os.getenv("FATSECRET2_CLIENT_SECRET")

# ==============================
# REST FRAMEWORK
# ==============================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ]
}

# ==============================
# LOGGING — hides stack traces in production
# ==============================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console" if DEBUG else "null"],
            "level": "INFO" if DEBUG else "ERROR",
        },
        "django.request": {
            "handlers": ["console" if DEBUG else "null"],
            "level": "WARNING" if DEBUG else "ERROR",
            "propagate": False,
        },
    },
}

# ==============================
# MISC
# ==============================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Australia/Sydney"
USE_I18N = True
USE_TZ = True
