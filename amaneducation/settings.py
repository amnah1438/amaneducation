from pathlib import Path
import os

# 1. المسارات الأساسية
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. الأمان
SECRET_KEY = 'django-insecure-f^#4+1-yrnoelle5gc++9#uq8$mqua6hi70p66_#@1#gk-z7lh'
DEBUG = True
ALLOWED_HOSTS = []

# 3. التطبيقات (INSTALLED_APPS)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # تطبيقات المحرر المطور
    'ckeditor',
    'ckeditor_uploader', 

    # تطبيقات المنصة الخاصة بك
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

# 4. الوسطاء (MIDDLEWARE)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

# 5. قاعدة البيانات
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 6. اللغة والتوقيت
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

# 7. الملفات الثابتة والوسائط (لضمان ظهور الصور والرموز)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# إعدادات رفع الصور
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_RESTRICT_BY_USER = False 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================================================
# ➕ إعدادات المحرر (CKEditor) - النسخة الاحترافية المخصصة
# ======================================================
CKEDITOR_CONFIGS = {
    # النسخة العلمية (للقدرات الكمي، الرياضيات، الفيزياء، الكيمياء)
    'scientific_editor': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'width': '100%',
        'height': '300px',
        'language': 'ar',
        'contentsLangDirection': 'rtl',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'TextColor', 'BGColor', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'JustifyRight', 'JustifyCenter', 'JustifyLeft'],
            '/', 
            # أيقونة WIRIS للرسم باليد والرموز المعقدة
            ['ckeditor_wiris_formulaEditor', 'Mathjax', 'SpecialChar', 'Table', 'HorizontalRule'], 
            ['Image', 'Link', 'Unlink', 'Maximize', 'Source'],
        ],
        'extraPlugins': ','.join([
            'mathjax', 'widget', 'lineutils', 'dialog', 'ckeditor_wiris', 'image2', 'uploadimage',
        ]),
        'mathJaxLib': 'https://cdn.jsdelivr.net/npm/mathjax@2.7.9/MathJax.js?config=TeX-AMS_HTML',
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
    },

    # النسخة الافتراضية (لباقي الأقسام - بسيطة كما كانت)
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'width': '100%',
        'height': '200px',
        'language': 'ar',
        'contentsLangDirection': 'rtl',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', '-', 'TextColor', 'BGColor', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'JustifyRight', 'JustifyCenter', 'JustifyLeft'],
            ['Image', 'Link', 'Unlink', 'Maximize'],
        ],
        'extraPlugins': ','.join(['image2', 'uploadimage']),
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
    },
}
