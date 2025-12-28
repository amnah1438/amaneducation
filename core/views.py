from django.shortcuts import render
from .models import SchoolSettings


def home(request):
    settings_obj = SchoolSettings.objects.first()
    return render(request, "core/home.html", {"settings": settings_obj})
