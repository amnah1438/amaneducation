"""
Core URLs — توجيه الصفحات العامة + لوحة المديرة.
"""
from django.contrib import admin as django_admin
from django.urls import path

from . import views

# عناوين Django admin (متروكة هنا فقط لتسهيل التشخيص).
django_admin.site.site_header = "إدارة منصة آمنة التعليمية"
django_admin.site.site_title = "منصة آمنة"

urlpatterns = [
    # ── تشخيص الصور (مؤقت) ──
    path('debug-images/', views.debug_images, name='debug_images'),
    # ── الصفحات العامة ─────────────────────────────────────────
    path('', views.home, name='home'),
    path('skill/<int:skill_id>/', views.skill_detail, name='skill_detail'),
    path('skill/<int:skill_id>/test/', views.take_test, name='take_test'),
    path('skill/<int:skill_id>/print/', views.skill_print, name='skill_print'),

    # ── تفعيل/إلغاء الاختبارات (AJAX, POST فقط) ─────────────────
    path('activate-exam/<int:exam_id>/', views.activate_exam, name='activate_exam'),
    path('deactivate-exam/<int:exam_id>/', views.deactivate_exam, name='deactivate_exam'),
    path('exam/<int:exam_id>/print/', views.exam_print, name='exam_print'),

    # ── لوحة المديرة (Enterprise V2 — الوحيدة) ─────────────────
    path('admin-dashboard/', views.admin_v2_dashboard, name='admin_dashboard'),
    path('admin-dashboard/data.json', views.admin_v2_data_json, name='admin_v2_data_json'),
    path('admin-dashboard/analytics.json', views.admin_analytics_json, name='admin_analytics_json'),
    path('admin-dashboard/report', views.admin_report, name='admin_report'),
    path('admin-dashboard/add-teacher/', views.admin_add_teacher, name='admin_add_teacher'),
    path('admin-dashboard/add-student/', views.admin_add_student, name='admin_add_student'),
    path('admin-dashboard/add-classroom/', views.admin_add_classroom, name='admin_add_classroom'),
    path('admin-dashboard/delete-classroom/<int:classroom_id>/', views.admin_delete_classroom, name='admin_delete_classroom'),
    path('admin-dashboard/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-dashboard/edit-user/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-dashboard/view-as/<int:user_id>/', views.admin_view_as, name='admin_view_as'),
    path('admin-dashboard/return/', views.admin_return, name='admin_return'),

    # ── إستيراد المعلمات والطالبات بـ Excel (لوحة المديرة) ────
    path('admin-dashboard/import-teachers/', views.admin_import_teachers, name='admin_import_teachers'),
    path('admin-dashboard/import-students/', views.admin_import_students, name='admin_import_students'),

    # ── الاختبارات الشاملة ──────────────────────────────────────
    path('admin-dashboard/comprehensive/', views.admin_comprehensive, name='admin_comprehensive'),
    path('admin-dashboard/add-comprehensive/', views.admin_add_comprehensive, name='admin_add_comprehensive'),
    path('admin-dashboard/comprehensive/<int:skill_id>/edit/', views.admin_edit_comprehensive, name='admin_edit_comprehensive'),
    path('admin-dashboard/comprehensive/<int:skill_id>/delete/', views.admin_delete_comprehensive, name='admin_delete_comprehensive'),
    path('admin-dashboard/comprehensive/<int:skill_id>/questions/', views.admin_comp_questions, name='admin_comp_questions'),
    path('admin-dashboard/comprehensive/<int:skill_id>/questions/add/', views.admin_comp_add_question, name='admin_comp_add_question'),
    path('admin-dashboard/comprehensive/<int:skill_id>/questions/import/', views.admin_comp_import_excel, name='admin_comp_import_excel'),
    path('admin-dashboard/comprehensive/<int:skill_id>/questions/<int:q_id>/delete/', views.admin_comp_delete_question, name='admin_comp_delete_question'),
    path('admin-dashboard/comprehensive/<int:skill_id>/questions/<int:q_id>/edit/', views.admin_comp_edit_question, name='admin_comp_edit_question'),
]
