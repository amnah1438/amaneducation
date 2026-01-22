from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # --- إضافة مسار رفع الصور للمحرر (CKEditor Uploader) ---
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Apps
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

# Media & Static (development only)
# تم دمج Static و Media لضمان ظهور صور المحرر والرموز بشكل صحيح
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
