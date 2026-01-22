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

    # مكتبة محرر النصوص المطور
    'ckeditor',

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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================================
# ➕ إعدادات محرر الرياضيات والنصوص (النسخة المنظمة)
# ======================================================
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'width': '100%',     # جعل المحرر يأخذ العرض الكامل لمنع التداخل
        'height': '180px',    # ارتفاع مريح جداً للكتابة
        'language': 'ar',    # واجهة المحرر باللغة العربية
        'toolbar_Custom': [
            # السطر الأول: أدوات التنسيق النصي (مثالية للقسم اللفظي)
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['JustifyRight', 'JustifyCenter', 'JustifyLeft', 'JustifyBlock'],
            
            '/', # هذا السطر يقوم بكسر الأدوات لسطر جديد لمنع الزحام في الخانات الضيقة
            
            # السطر الثاني: أدوات الرياضيات والوسائط (مثالية للقسم الكمي والتحصيلي)
            ['Mathjax', 'SpecialChar'],
            ['Link', 'Unlink', 'Image', 'Table', 'HorizontalRule'],
            ['Source', 'Maximize'], # زر Maximize يتيح للمعلمة الكتابة في شاشة كاملة
        ],
        'extraPlugins': ','.join([
            'mathjax',      # تفعيل أيقونة الرياضيات
            'widget',       # لتنظيم العناصر داخل النص
            'lineutils',    # لتحسين مظهر الخطوط
            'dialog',       # لفتح نوافذ الإضافة بشكل مرتب
        ]),
        'mathJaxLib': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
    },
}
