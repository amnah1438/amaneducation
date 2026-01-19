from django.contrib import admin
from .models import Profile

# هنا نترك فقط إدارة ملفات المستخدمين الخاصة بتطبيق accounts
# ونحذف أي تسجيل لـ Skill أو Teacher لأنه موجود في تطبيق core
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "pin_code")
    list_filter = ("role",)