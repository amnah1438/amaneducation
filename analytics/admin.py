from django.contrib import admin
from .models import DailyStat


@admin.register(DailyStat)
class DailyStatAdmin(admin.ModelAdmin):
    list_display = ("date", "attempts_count", "avg_score")
