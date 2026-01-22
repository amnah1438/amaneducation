from django.urls import path
from . import views

urlpatterns = [
    # مسار الصفحة الرئيسية
    path("", views.home, name="home"),
    
    # مسار صفحة الدرس/المهارة
    path("skill/<int:skill_id>/", views.skill_detail, name="skill_detail"),

    # المسار الجديد الذي أضفته لكِ لفتح صفحة الاختبار
    path("skill/<int:skill_id>/test/", views.take_test, name="take_test"),
]
