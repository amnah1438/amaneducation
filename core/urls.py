"""
Core URLs — توجيه الصفحات العامة + لوحة المديرة.

تنظيفات هامة:
- حُذفت مسارات `admin/` و `ckeditor/` لأنها معرّفة في amaneducation/urls.py
  (التعريف المزدوج كان يتسبّب بتنازع NamespaceWarning).
- وُحّدت الإزاحات (كان الملف غير منتظم — مشكلة قراءة، ليست syntactic).
- أُضيف namespace ضمني عبر تجميع المسارات منطقياً.
"""
from django.contrib import admin as django_admin
from django.urls import path

from . import views

# عناوين Django admin (متروكة هنا فقط لتسهيل التشخيص).
django_admin.site.site_header = "إدارة منصة آمنة التعليمية"
django_admin.site.site_title = "منصة آمنة"

urlpatterns = [
    # ── الصفحات العامة ─────────────────────────────────────────
    path('', views.home, name='home'),
    path('skill/<int:skill_id>/', views.skill_detail, name='skill_detail'),
    path('skill/<int:skill_id>/test/', views.take_test, name='take_test'),

    # ── تفعيل/إلغاء الاختبارات (AJAX, POST فقط) ─────────────────
    path('activate-exam/<int:exam_id>/', views.activate_exam, name='activate_exam'),
    path('deactivate-exam/<int:exam_id>/', views.deactivate_exam, name='deactivate_exam'),

    # ── لوحة المديرة ────────────────────────────────────────────
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/add-teacher/', views.admin_add_teacher, name='admin_add_teacher'),
    path('admin-dashboard/add-student/', views.admin_add_student, name='admin_add_student'),
    path('admin-dashboard/add-classroom/', views.admin_add_classroom, name='admin_add_classroom'),
    path('admin-dashboard/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-dashboard/view-as/<int:user_id>/', views.admin_view_as, name='admin_view_as'),
    path('admin-dashboard/return/', views.admin_return, name='admin_return'),

    # ── الاختبارات الشاملة ──────────────────────────────────────
    path('admin-dashboard/comprehensive/', views.admin_comprehensive, name='admin_comprehensive'),
    path('admin-dashboard/add-comprehensive/', views.admin_add_comprehensive, name='admin_add_comprehensive'),
]
