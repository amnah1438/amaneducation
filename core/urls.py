from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

admin.site.site_header = "إدارة منصة آمنة التعليمية"
admin.site.site_title = "منصة آمنة"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("skill/<int:skill_id>/", views.skill_detail, name="skill_detail"),
    path("skill/<int:skill_id>/test/", views.take_test, name="take_test"),
    path('activate-exam/<int:exam_id>/', views.activate_exam, name='activate_exam'),
    path('admin-dashboard/add-classroom/', views.admin_add_classroom, name='admin_add_classroom'),
    path('deactivate-exam/<int:exam_id>/', views.deactivate_exam, name='deactivate_exam'),
    path('admin-dashboard/add-comprehensive/', views.admin_add_comprehensive, name='admin_add_comprehensive'),
path('admin-dashboard/comprehensive/', views.admin_comprehensive, name='admin_comprehensive'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
   path('admin-dashboard/view-as/<int:user_id>/', views.admin_view_as, name='admin_view_as'),
path('admin-dashboard/return/', views.admin_return, name='admin_return'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('admin-dashboard/add-teacher/', views.admin_add_teacher, name='admin_add_teacher'),
path('admin-dashboard/add-student/', views.admin_add_student, name='admin_add_student'),
path('admin-dashboard/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)