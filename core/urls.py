from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.site_header), # مسار لوحة الإدارة
    path('admin/', admin.site.urls),
    
    # مسارات المنصة الأساسية
    path("", views.home, name="home"),
    path("skill/<int:skill_id>/", views.skill_detail, name="skill_detail"),
    path("skill/<int:skill_id>/test/", views.take_test, name="take_test"),

    # --- رابط مكتبة رفع الصور (ضروري جداً لعمل المحرر) ---
    path('ckeditor/', include('ckeditor_uploader.urls')),

]

# --- إعدادات عرض الصور والملفات المرفوعة أثناء التطوير ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
