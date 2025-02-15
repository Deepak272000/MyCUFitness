import os
from pathlib import Path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import staticfiles
from dotenv import load_dotenv, dotenv_values
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()  # Ensure the .env file is loaded

env = environ.Env()
environ.Env.read_env()

config = dotenv_values(".env")

SECRET_KEY = "your-secret-key"
AUTH_USER_MODEL = 'users.User'
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_otp",
    "django_otp.plugins.otp_totp",
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    "allauth.socialaccount",
    'allauth.socialaccount.providers.google',
    'social_django',
    'oauth2_provider',
    "users",
    "workouts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = "MyCUFitness.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "mycufitness",
        "USER": "root",
        "PASSWORD": "12345",
        "HOST": "localhost",
        "PORT": "3306",
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    'social_core.backends.google.GoogleOAuth2',
]

# JWT Authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework.authentication.SessionAuthentication',  # Django session login
        'rest_framework.authentication.BasicAuthentication',
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # Ensure authentication is required
    ),
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [os.path.join(BASE_DIR, "templates")],  # Ensure you have this line
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "codecrafters2025coen@gmail.com"
EMAIL_HOST_PASSWORD = "vdcu srvq kdat giyp"



SITE_ID = 4
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = 'login'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/dashboard/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/login/"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config["GOOGLE_CLIENT_ID"]
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config["GOOGLE_CLIENT_SECRET"]

# OTP / 2FA Settings
OTP_TOTP_ISSUER = "MyCUFitness"

SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Ensure sessions are stored in DB
SESSION_COOKIE_AGE = 86400  # Keep user logged in for 1 day
SESSION_SAVE_EVERY_REQUEST = True  # Save session on every request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Don't log out when browser is closed

ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"
SOCIALACCOUNT_ADAPTER = "allauth.socialaccount.adapter.DefaultSocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = True  # Ensure new users get created

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
