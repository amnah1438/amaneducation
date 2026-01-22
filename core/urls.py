from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# ضعيه هنا خارج المصفوفة وليس داخل path
admin.site.site_header = "إدارة منصة آمنة التعليمية"

urlpatterns = [
    # تأكدي أن السطر مكتوب هكذا فقط:
    path('admin/', admin.site.urls),
    
    # مسارات المنصة
    path("", views.home, name="home"),
    path("skill/<int:skill_id>/", views.skill_detail, name="skill_detail"),
    path("skill/<int:skill_id>/test/", views.take_test, name="take_test"),

    # رابط رفع الصور
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# إعدادات ملفات الميديا
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
