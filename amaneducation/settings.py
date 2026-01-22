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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ckeditor',
    'ckeditor_uploader', 

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

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================================
# ➕ إعدادات المحرر النهائية (منظمة بـ 3 أسطر لمنع الاختفاء)
# ======================================================
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'width': '100%',
        'height': '220px', # ارتفاع مناسب لا يغطي الأسئلة
        'language': 'ar',
        'contentsLangDirection': 'rtl',
        'toolbar_Custom': [
            # السطر الأول: التنسيق اللفظي الأساسي
            ['Bold', 'Italic', 'Underline', '-', 'TextColor', 'BGColor', '-', 'RemoveFormat'],
            ['JustifyRight', 'JustifyCenter', 'JustifyLeft', '-', 'NumberedList', 'BulletedList'],
            '/', # سطر جديد
            
            # السطر الثاني: الرياضيات والرموز والسبورة
            ['ckeditor_wiris_formulaEditor', 'Mathjax', 'SpecialChar'],
            ['Subscript', 'Superscript', 'Table', 'HorizontalRule'],
            '/', # سطر جديد
            
            # السطر الثالث: الصور والتحكم
            ['Image', 'Link', 'Unlink', '-', 'Source', 'Maximize'],
        ],
        'extraPlugins': ','.join([
            'mathjax', 
            'widget', 
            'lineutils', 
            'dialog', 
            'ckeditor_wiris', # سبورة الرسم بالفأرة
            'image2', 
            'uploadimage',
            'colorbutton',
        ]),
        'mathJaxLib': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
        
        # رموز عربية جاهزة
        'specialChars': ['≥', '≤', '>', '<', '|', '√', '²', '³', 'π', 'س', 'ص', 'ع'],
    },
}
