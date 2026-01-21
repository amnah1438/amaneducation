from django.urls import path
from . import views

urlpatterns = [
    # مسار الصفحة الرئيسية (شغلك السابق)
    path("", views.home, name="home"),
    
    # المسار الجديد لفتح صفحة الدرس/المهارة عند الضغط على البطاقة
    path("skill/<int:skill_id>/", views.skill_detail, name="skill_detail"),
]
