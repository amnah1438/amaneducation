from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('result/<int:result_id>/', views.student_result_view, name='student_result_view'),
    path('import/', views.import_students_excel, name='import_students_excel'),
    # إضافة يدوية لطالبة واحدة (POST من نموذج صفحة الاستيراد)
    path('import/add-manual/', views.add_student_manual, name='add_student_manual'),
    path('manage/', views.manage_students, name='manage_students'),
]