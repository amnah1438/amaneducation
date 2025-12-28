from django.contrib import admin
from .models import Student, ClassRoom


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "classroom")
    list_filter = ("classroom",)
