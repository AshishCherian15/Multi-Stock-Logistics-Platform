from pathlib import Path
import os
import sys
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# Add apps folder to Python path
APPS_DIR = BASE_DIR / 'apps'
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)

# Hosts: add your own Render subdomain and custom domains here
ALLOWED_HOSTS = [
    '.vercel.app',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    *config('EXTRA_ALLOWED_HOSTS', default='', cast=Csv()),  # add custom domains via env
]

# Suppress specific 404 errors
IGNORABLE_404_URLS = [
    r'\.well-known/appspecific/com\.chrome\.devtools\.json$',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'goods',
    'stock',
    'warehouse',
    'customer',
    'supplier',
    'auth_system',
    'barcode',
    'orders',
    'notifications',
    'reports',
    'pos',
    'expenses',
    'inventory',
    'messaging',
    'rentals',
    'storage',
    'lockers',
    'credit',
    'coupons',
    'audit',
    'categories',
    'billing',
    'users',
    'permissions',
    'team',
    'analytics',
    'cart',
    'wishlist',
    'payments',
    'settings',
    'search',
    'dashboard',
    'shipping',
    'forums',
    'about',
    'profile',
    'reviews',
    'tickets',
    'admin_panel',
    'supervisor_panel',
    'staff_panel',
    'guest',
    'superadmin_panel',
    'quotations',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'auth_system.middleware.RoleBasedAccessMiddleware',
    'audit.middleware.AuditLogMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'greaterwms.urls'

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
                'permissions.context_processors.user_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'greaterwms.wsgi.application'

import dj_database_url

# DATABASE_URL is set in Render / local .env for Supabase.
# In production, force explicit DATABASE_URL to avoid silent fallback to SQLite.
DATABASE_URL = config('DATABASE_URL', default='').strip()
if not DEBUG and not DATABASE_URL:
    raise RuntimeError('DATABASE_URL must be set when DEBUG=False')

database_default = DATABASE_URL or f'sqlite:///{BASE_DIR / "db.sqlite3"}'

DATABASES = {
    'default': dj_database_url.config(
        default=database_default,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=config('DB_SSL_REQUIRE', default=not DEBUG, cast=bool),
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CORS – allow all origins in DEBUG; restrict to explicit list in production
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        o.strip()
        for o in config('CORS_ALLOWED_ORIGINS', default='').split(',')
        if o.strip()
    ]
    # Always allow Vercel previews and the Render service itself
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r'^https://.*\.vercel\.app$',
        r'^https://.*\.onrender\.com$',
    ]
CORS_ALLOW_CREDENTIALS = True
LOGIN_URL = '/auth/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Django Allauth Configuration
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

ACCOUNT_LOGIN_ON_GET = False
ACCOUNT_LOGOUT_ON_GET = False
SOCIALACCOUNT_LOGIN_ON_GET = False

# Session Settings - Force logout on server restart
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# CSRF / Security Settings
CSRF_COOKIE_SECURE = not DEBUG          # True in production (HTTPS)
CSRF_COOKIE_HTTPONLY = False            # Needs to be readable by JS for AJAX
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG       # True in production
SECURE_SSL_REDIRECT = not DEBUG         # Redirect HTTP -> HTTPS on Render
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Supabase / Render trusted origins (CSRF for POST from frontend)
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.onrender.com',
    *[
        o.strip()
        for o in config('CSRF_TRUSTED_ORIGINS_EXTRA', default='').split(',')
        if o.strip()
    ],
]

# Email Settings - Real SMTP with secure credentials
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=f'MultiStock Platform <{config("EMAIL_HOST_USER", default="noreply@multistock.com")}>')
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 30

# If no credentials provided, fall back to console
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'