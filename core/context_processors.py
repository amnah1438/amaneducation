from core.models import SchoolSettings


def platform_settings(request):
    """يرسل إعدادات المنصة لكل القوالب تلقائياً"""
    try:
        settings_obj = SchoolSettings.objects.first()
    except Exception:
        settings_obj = None

    return {
        'platform': settings_obj,
    }
