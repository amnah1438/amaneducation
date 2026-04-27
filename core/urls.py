from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# تخصيص عنوان لوحة الإدارة (يظهر في أعلى الصفحة)
admin.site.site_header = "إدارة منصة آمنة التعليمية"
admin.site.site_title = "منصة آمنة"

urlpatterns = [
    # 1. مسار لوحة الإدارة (سطر واحد فقط)
    path('admin/', admin.site.urls),
    
    # 2. مسارات المنصة الأساسية (الدروس والاختبارات)
    path("", views.home, name="home"),
    path("skill/<int:skill_id>/", views.skill_detail, name="skill_detail"),
    path("skill/<int:skill_id>/test/", views.take_test, name="take_test"),
path('activate-exam/<int:exam_id>/', views.activate_exam, name='activate_exam'),
path('deactivate-exam/<int:exam_id>/', views.deactivate_exam, name='deactivate_exam'),
path('skill/<int:skill_id>/', views.skill_detail, name='skill_detail'),
path('activate-exam/<int:exam_id>/', views.activate_exam, name='activate_exam'),
path('deactivate-exam/<int:exam_id>/', views.deactivate_exam, name='deactivate_exam'),
    # 3. رابط مكتبة رفع الصور (ضروري جداً لعمل المحرر ورفع صور المعلمات)
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# 4. إعدادات عرض الصور والملفات المرفوعة (Media) والملفات الثابتة (Static)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
