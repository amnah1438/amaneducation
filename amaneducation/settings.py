import os
from pathlib import Path

# 1. المسارات الأساسية للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. إعدادات الأمان
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-f^#4+1-yrnoelle5gc++9#uq8$mqua6hi70p66_#@1#gk-z7lh')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = ['*']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# 3. التطبيقات المثبتة
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Cloudinary لتخزين الصور (يجب أن يكون قبل staticfiles)
    'cloudinary_storage',
    'cloudinary',

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

# 4. الوسطاء (Middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
                'core.context_processors.platform_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'amaneducation.wsgi.application'

# 6. قاعدة البيانات
# في الإنتاج (Render): يستخدم PostgreSQL بالقيم المنفردة
# محلياً: يستخدم SQLite
if os.environ.get('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
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

# 9. الملفات الثابتة والوسائط
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
# ➕ إعدادات المحرر الاحترافية (تعديل الأقسام)
# ======================================================
CKEDITOR_CONFIGS = {
    # 1. النسخة العلمية (للقدرات والتحصيلي): تشمل (الصور، الجداول، الروابط، والرموز)
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
            ['Image', 'Table', 'Link', 'Unlink'], # صور وجداول وروابط
            ['Mathjax', 'SpecialChar', 'HorizontalRule', 'Maximize', 'Source'], # رموز رياضية
        ],
        'extraPlugins': ','.join([
            'mathjax', 'widget', 'lineutils', 'dialog', 'image2', 'uploadimage',
        ]),
        'mathJaxLib': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
    },
    
    # 2. النسخة الافتراضية (لباقي الأقسام): تشمل (الصور، الجداول، الروابط) فقط
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'width': '100%',
        'height': '200px',
        'language': 'ar',
        'contentsLangDirection': 'rtl',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'JustifyRight', 'JustifyCenter', 'JustifyLeft'],
            ['Image', 'Table', 'Link', 'Unlink'], # صور وجداول وروابط فقط (بدون أزرار رياضيات)
            ['Maximize', 'Source'],
        ],
        'extraPlugins': ','.join([
            'widget', 'lineutils', 'dialog', 'image2', 'uploadimage',
        ]),
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# إعدادات تسجيل الدخول
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ======================================================
# إعدادات Cloudinary (تخزين الصور والملفات)
# ======================================================
import cloudinary
import cloudinary.uploader
import cloudinary.api

# دعم CLOUDINARY_URL (الصيغة اللي يستخدمها Render تلقائياً)
# مثال: cloudinary://489947491336852:ybw_lynZTuhxcRbbQ1NfIVZT9r8@dyg4401o9
_cld_url = os.environ.get('CLOUDINARY_URL', '')
if _cld_url:
    # CLOUDINARY_URL موجود — cloudinary.config يقرأها تلقائي
    import re as _re
    _m = _re.match(r'cloudinary://([^:]+):([^@]+)@(.+)', _cld_url)
    if _m:
        _cld_key, _cld_secret, _cld_name = _m.group(1), _m.group(2), _m.group(3)
    else:
        _cld_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dyg4401o9')
        _cld_key = os.environ.get('CLOUDINARY_API_KEY', '489947491336852')
        _cld_secret = os.environ.get('CLOUDINARY_API_SECRET', 'ybw_lynZTuhxcRbbQ1NfIVZT9r8')
else:
    _cld_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dyg4401o9')
    _cld_key = os.environ.get('CLOUDINARY_API_KEY', '489947491336852')
    _cld_secret = os.environ.get('CLOUDINARY_API_SECRET', 'ybw_lynZTuhxcRbbQ1NfIVZT9r8')

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': _cld_name,
    'API_KEY': _cld_key,
    'API_SECRET': _cld_secret,
}

# تهيئة Cloudinary مباشرة (مطلوب لعمل الرفع)
cloudinary.config(
    cloud_name=_cld_name,
    api_key=_cld_key,
    api_secret=_cld_secret,
    secure=True,
)

# طباعة تشخيصية عند بدء التشغيل
print(f"☁️ Cloudinary config: cloud={_cld_name}, key={_cld_key[:6]}..., CLOUDINARY_URL={'SET' if _cld_url else 'NOT SET'}")

# استخدم Cloudinary دائماً لتخزين ملفات الوسائط (محلي + إنتاج)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ======================================================
# إعدادات الإنتاج (Render)
# ======================================================
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # WhiteNoise for static files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'