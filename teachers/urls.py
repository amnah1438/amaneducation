from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # 🔹 Dashboard
    # =========================
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # =========================
    # 🔹 Skills Management
    # =========================
    path('skills/', views.skill_manager, name='skill_manager'),

    # ❗ تأكد أن الاسم مطابق للدالة عندك في views.py
    path('skills/add/', views.add_skill_complete, name='add_skill'),

    path('skills/add-complete/', views.add_skill_complete, name='add_skill_complete'),

    path('skills/delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),

    # =========================
    # 🔹 Exams
    # =========================
    path('exam/<int:exam_id>/add-question/', views.add_question, name='add_question'),

    path('exam/<int:exam_id>/import/', views.import_questions_excel, name='import_questions_excel'),

    # =========================
    # 🔹 Results
    # =========================
    path('exam/<int:exam_id>/results/', views.exam_results, name='exam_results'),

    path('result/<int:result_id>/', views.student_result, name='student_result'),

    path('result/<int:result_id>/score/', views.enter_manual_score, name='enter_manual_score'),

    # =========================
    # 🔹 Sessions
    # =========================
    path('sessions/add/', views.add_session, name='add_session'),
]