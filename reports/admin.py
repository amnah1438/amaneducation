from django.contrib import admin
from .models import ReportFile


@admin.register(ReportFile)
class ReportFileAdmin(admin.ModelAdmin):
    list_display = ("attempt", "created_at")
