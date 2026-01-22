from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. لوحة الإدارة
    path('admin/', admin.site.urls),

    # 2. مسار رفع ملفات وصور المحرر (حل مشكلة تبويب الرفع المفقود)
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # 3. تطبيقات المنصة (التوجيه للروابط الفرعية)
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('skills/', include('skills.urls')),
    path('lessons/', include('lessons.urls')),
    path('question-bank/', include('question_bank.urls')),
    path('assessments/', include('assessments.urls')),
    path('reports/', include('reports.urls')),
    path('analytics/', include('analytics.urls')),
    path('qr/', include('qr_access.urls')),
]

# 4. تفعيل مسارات الوسائط والملفات الثابتة (ضروري لظهور صور الأسئلة والرموز)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
