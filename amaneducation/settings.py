import os
from pathlib import Path

# 1. المسارات الأساسية للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. إعدادات الأمان (تأكدي من عدم تغيير الـ Key الخاص بك)
SECRET_KEY = 'django-insecure-f^#4+1-yrnoelle5gc++9#uq8$mqua6hi70p66_#@1#gk-z7lh'
DEBUG = True
ALLOWED_HOSTS = ['*'] # للسماح بالتشغيل المحلي

# 3. التطبيقات المثبتة (مهم جداً ترتيب CKEditor)
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

    # تطبيقات المنصة الخاصة بك (تأكدي أن الأسماء مطابقة لمجلداتك)
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

# 4. الوسطاء (Middleware)
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

# 5. القوالب (Templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# 6. قاعدة البيانات (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 8. اللغة والتوقيت
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 9. الملفات الثابتة والوسائط (حل مشكلة "المصدر مفقود")
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 10. إعدادات رفع CKEditor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_RESTRICT_BY_USER = False 
CKEDITOR_BROWSE_SHOW_METADATA = True

# ======================================================
# ➕ إعدادات المحرر الاحترافية (للقدرات والتحصيلي)
# ======================================================
CKEDITOR_CONFIGS = {
    'scientific_editor': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'width': '100%',
        'height': '250px',
        'language': 'ar',
        'contentsLangDirection': 'rtl',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'TextColor', 'BGColor', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'JustifyRight', 'JustifyCenter', 'JustifyLeft'],
            '/', 
            # أيقونة السيجما للرياضيات والجداول
            ['Mathjax', 'SpecialChar', 'Table', 'HorizontalRule'], 
            ['Image', 'Link', 'Unlink', 'Maximize', 'Source'],
        ],
        'extraPlugins': ','.join([
            'mathjax', 'widget', 'lineutils', 'dialog', 'image2', 'uploadimage',
        ]),
        # رابط مكتبة الرياضيات (MathJax) ليعمل بدون مشاكل Terminal
        'mathJaxLib': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
        
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
    },
    
    'default': {
        'toolbar': 'Full',
        'height': '200px',
        'width': '100%',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
