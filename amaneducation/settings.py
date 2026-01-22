from pathlib import Path
import os

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
# 📦 التطبيقات (INSTALLED_APPS)
# =========================
INSTALLED_APPS = [
    # Django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # مكتبة محرر النصوص المطور ورفع الصور
    'ckeditor',
    'ckeditor_uploader', 

    # تطبيقات المشروع الأساسية
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
# 🧱 الوسطاء (MIDDLEWARE)
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
# 🌐 الروابط والقوالب
# =========================
ROOT_URLCONF = 'amaneducation.urls'

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
# 🌍 اللغة والتوقيت
# =========================
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True


# =========================
# 📁 الملفات الثابتة والرفع
# =========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# إعدادات رفع الصور الخاصة بالمحرر
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow" # للتأكد من معالجة الصور بشكل صحيح

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================================
# ➕ إعدادات محرر الرياضيات والرسم والرفع (النسخة الاحترافية)
# ======================================================
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'width': '100%',
        'height': '250px',
        'language': 'ar',
        'contentsLangDirection': 'rtl',
        'toolbar_Custom': [
            # السطر الأول: التنسيق
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'JustifyRight', 'JustifyCenter', 'JustifyLeft'],
            '/', 
            # السطر الثاني: الرسم باليد والرموز والصور
            ['ckeditor_wiris_formulaEditor', 'Mathjax', 'SpecialChar'], # علامة WIRIS هي التي تفتح الرسم باليد
            ['Image', 'Table', 'HorizontalRule'],
            ['Source', 'Maximize'],
        ],
        'extraPlugins': ','.join([
            'mathjax',      # المعادلات بالكود
            'widget',
            'lineutils',
            'dialog',
            'ckeditor_wiris', # تفعيل الرسم باليد بالفأرة
            'uploadimage',    # تفعيل سحب وإفلات الصور
        ]),
        'mathJaxLib': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
        
        # تفعيل تبويب "الرفع" في نافذة الصور
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
        
        # تخصيص الرموز العربية السريعة
        'specialChars': ['≥', '≤', '>', '<', '|', '√', '²', '³', 'π', 'س', 'ص', 'ع'],
    },
}
