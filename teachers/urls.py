from django.urls import path
from . import views

urlpatterns = [
    # ─── Dashboard ──────────────────────────────────────────────
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # ─── Skills Management ──────────────────────────────────────
    path('skills/', views.skill_manager, name='skill_manager'),
    path('skills/add/', views.add_skill_complete, name='add_skill'),
    path('skills/add-complete/', views.add_skill_complete, name='add_skill_complete'),
    path('skills/<int:skill_id>/edit/', views.edit_skill, name='edit_skill'),
    path('skills/<int:skill_id>/view/', views.view_skill, name='view_skill'),
    path('skills/delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('skill/<int:skill_id>/questions/', views.get_skill_questions, name='get_skill_questions'),
    path('skills/import/', views.import_skills_excel, name='import_skills_excel'),
    path('skills/<int:skill_id>/use/', views.use_shared_skill, name='use_shared_skill'),

    # ─── Exams ─────────────────────────────────────────────────
    path('exam/<int:exam_id>/add-question/', views.add_question, name='add_question'),
    path('exam/<int:exam_id>/edit-question/<int:q_id>/', views.edit_question, name='edit_question'),
    path('exam/<int:exam_id>/delete-question/<int:q_id>/', views.delete_question, name='delete_question'),
    path('exam/<int:exam_id>/import/', views.import_questions_excel, name='import_questions_excel'),

    # ─── Results ───────────────────────────────────────────────
    path('exam/<int:exam_id>/results/', views.exam_results, name='exam_results'),
    path('result/<int:result_id>/', views.student_result, name='student_result'),
    path('result/<int:result_id>/score/', views.enter_manual_score, name='enter_manual_score'),

    # ─── Sessions ─────────────────────────────────────────────
    path('sessions/add/', views.add_session, name='add_session'),

    # ─── Classrooms ───────────────────────────────────────────
    path('classrooms/', views.manage_classrooms, name='manage_classrooms'),
    path('classrooms/<int:classroom_id>/students/', views.get_classroom_students, name='get_classroom_students'),

    # ─── APIs ─────────────────────────────────────────────────
    path('dashboard/student-report.json', views.teacher_student_report_json, name='teacher_student_report_json'),
    path('api/skill-standards.json', views.skill_standards_json, name='skill_standards_json'),
    path('api/skill-standards/manage/', views.manage_skill_standard, name='manage_skill_standard'),
    path('api/gap-analysis.json', views.gap_analysis_json, name='gap_analysis_json'),

    # ─── Manual Score Entry ───────────────────────────────────
    path('manual-score/', views.manual_score_entry, name='manual_score_entry'),

    # ─── PDF Proxy ────────────────────────────────────────────
    path('skill-pdf/<int:content_id>/', views.serve_skill_pdf, name='serve_skill_pdf'),
]
