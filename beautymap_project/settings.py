"""
BeautyMap Congo — Django Settings
"""
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-beautymap-congo-change-in-production-xyz123')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'channels',
    # Local apps
    'apps.accounts',
    'apps.shops',
    'apps.bookings',
    'apps.reviews',
    'apps.messaging',
    'apps.notifications',
    'apps.payments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beautymap_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'beautymap_project.wsgi.application'
ASGI_APPLICATION = 'beautymap_project.asgi.application'

# ── Base de données MySQL ─────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'beautymap_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ── Jazzmin (interface admin) ─────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title":           "BeautyMap Admin",
    "site_header":          "BeautyMap Congo",
    "site_brand":           "BeautyMap",
    "welcome_sign":         "Bienvenue dans le panneau admin",
    "site_logo":            "images/logo.png",
    "login_logo":           "images/logo.png",
    "show_sidebar":         True,
    "navigation_expanded":  True,
    "icons": {
        "shops.Shop":     "fas fa-store",
        "reviews.Review": "fas fa-star",
        "auth.User":      "fas fa-user",
    },
}

# ── Auth ──────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Localisation ──────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Brazzaville'
USE_I18N      = True
USE_TZ        = True

# ── Fichiers statiques ────────────────────────────────────
STATIC_URL      = '/static/'
STATIC_ROOT     = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# En développement : StaticFilesStorage (pas besoin de collectstatic)
# En production    : remplacer par whitenoise.storage.CompressedManifestStaticFilesStorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── REST Framework ────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

# ── CORS ──────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config(
    'CORS_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ── Django Channels (WebSocket) ───────────────────────────
# En dev Windows : InMemoryChannelLayer (pas besoin de Redis)
# En production  : passer à RedisChannelLayer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ── Celery (désactivé en dev local) ──────────────────────
CELERY_BROKER_URL    = config('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379')
CELERY_TIMEZONE      = 'Africa/Brazzaville'

# ── Email ─────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'lizagabriela80@gmail.com'
EMAIL_HOST_PASSWORD = 'piut nfam oriv axaf'
DEFAULT_FROM_EMAIL  = 'BeautyMap Congo <lizagabriela80@gmail.com>'

# ── SMS Africa's Talking ──────────────────────────────────
AT_API_KEY  = config('AT_API_KEY',  default='')
AT_USERNAME = config('AT_USERNAME', default='sandbox')
AT_SENDER   = config('AT_SENDER',   default='BeautyMap')

# ── Twilio WhatsApp (optionnel) ───────────────────────────
TWILIO_ACCOUNT_SID   = config('TWILIO_ACCOUNT_SID',   default='')
TWILIO_AUTH_TOKEN    = config('TWILIO_AUTH_TOKEN',     default='')
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM',  default='+14155238886')

# ── Crispy Forms ──────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK          = 'bootstrap5'

# ── Auth redirections ─────────────────────────────────────
LOGIN_URL           = '/auth/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ── Sessions ──────────────────────────────────────────────
SESSION_COOKIE_AGE      = 86400 * 30   # 30 jours
SESSION_SAVE_EVERY_REQUEST = True

# ── OTP ───────────────────────────────────────────────────
OTP_EXPIRY_MINUTES = 5
OTP_LENGTH         = 6