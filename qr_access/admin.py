from django.contrib import admin
from .models import QRSession


@admin.register(QRSession)
class QRSessionAdmin(admin.ModelAdmin):
    list_display = ("token", "teacher", "classroom", "skill", "expires_at", "is_active")
    list_filter = ("is_active",)
