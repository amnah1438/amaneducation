from django.contrib import admin
from .models import SchoolSettings


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "platform_name",
        "principal_name",
        "updated_at",
    )
