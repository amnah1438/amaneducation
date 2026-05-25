from core.models import SchoolSettings
from cloudinary.utils import cloudinary_url


def _get_logo_url(field_value):
    """يحوّل CloudinaryField إلى رابط صورة كامل"""
    if not field_value:
        return ''
    # CloudinaryField يخزّن public_id فقط
    val = str(field_value)
    if val.startswith('http'):
        return val
    # نبني رابط Cloudinary يدوياً
    url, _ = cloudinary_url(val)
    return url or ''


class SettingsProxy:
    """كائن وسيط يوفّر ministry_logo_url و school_logo_url مع باقي الحقول"""
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, name):
        if name == '_obj':
            return super().__getattribute__('_obj')
        return getattr(self._obj, name)

    def __bool__(self):
        return self._obj is not None

    @property
    def ministry_logo_url(self):
        if self._obj and self._obj.ministry_logo:
            return _get_logo_url(self._obj.ministry_logo)
        return ''

    @property
    def school_logo_url(self):
        if self._obj and self._obj.school_logo:
            return _get_logo_url(self._obj.school_logo)
        return ''


def platform_settings(request):
    """يرسل إعدادات المنصة لكل القوالب تلقائياً"""
    try:
        settings_obj = SchoolSettings.objects.first()
    except Exception:
        settings_obj = None

    proxy = SettingsProxy(settings_obj) if settings_obj else None

    return {
        'platform': proxy,
        'settings': proxy,
    }
