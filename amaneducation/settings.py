from pathlib import Path

# =========================
# 📁 المسار الأساسي
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# 🔐 الأمان
# =========================
SECRET_KEY = 'django-insecure-f^#4+1-yrnoelle5gc++9#uq8$mqua6hi70p66_#@1#gk-z7lh'

DEBUG = True

ALLOWED_HOSTS = []


# =========================
# 📦 التطبيقات
# =========================
INSTALLED_APPS = [
    # Django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project Apps
    'core',
    'accounts',
    'students',
    'teachers',
    'skills',
    'lessons',
    'question_bank',
    'assessments',
    'reports',
    'analytics',
    'qr_access',
]


# =========================
# 🧱 الوسطاء
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================
# 🌐 الروابط
# =========================
ROOT_URLCONF = 'amaneducation.urls'


# =========================
# 🖼️ القوالب
# =========================
# ✅ تم تعريف مجلد القوالب العام:
# /Users/amnah/aman education/amaneducation/templates
# وهو يساوي: BASE_DIR / "templates"
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # قوالب عامة للمشروع كله
        'DIRS': [
            BASE_DIR / 'templates',
        ],

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


# =========================
# 🚀 WSGI
# =========================
WSGI_APPLICATION = 'amaneducation.wsgi.application'


# =========================
# 🗄️ قاعدة البيانات
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================
# 🔑 التحقق من كلمات المرور
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================
# 🌍 اللغة والتوقيت
# =========================
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'

USE_I18N = True
USE_TZ = True


# =========================
# 📁 الملفات الثابتة
# =========================
STATIC_URL = '/static/'

# ✅ تأكدي أن مجلد static موجود داخل BASE_DIR
# /Users/amnah/aman education/amaneducation/static
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =========================
# 📁 ملفات الرفع (media)
# =========================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================
# 🆔 الإعداد الافتراضي للمفاتيح
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
