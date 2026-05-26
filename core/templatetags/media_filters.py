"""
Custom template filters for media handling:
- youtube_embed: convert any YouTube/Drive/Vimeo URL to a valid embeddable URL.
- safe_video_url: alias.

السبب: المتصفّح يرفض تضمين روابط مثل
  youtube.com/watch?v=XXXX  أو  youtu.be/XXXX
داخل <iframe> فتظهر شاشة سوداء.
الحل: نحوّلها إلى   youtube.com/embed/XXXX
بنفس المنطق نتعامل مع روابط Google Drive و Vimeo.
"""
import re
from urllib.parse import urlparse, parse_qs

from django import template

register = template.Library()


_YT_HOSTS = ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be')
_VIMEO_HOSTS = ('vimeo.com', 'www.vimeo.com', 'player.vimeo.com')
_DRIVE_HOSTS = ('drive.google.com',)


def _extract_youtube_id(url):
    """يستخرج معرف فيديو YouTube من أي صيغة رابط."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None

    # 1) youtu.be/<ID>
    if parsed.netloc.lower().endswith('youtu.be'):
        return parsed.path.lstrip('/').split('/')[0] or None

    # 2) youtube.com/watch?v=<ID>
    if 'youtube' in parsed.netloc.lower():
        if parsed.path == '/watch':
            qs = parse_qs(parsed.query)
            v = qs.get('v')
            if v:
                return v[0]

        # 3) youtube.com/embed/<ID>  (already embed)
        if parsed.path.startswith('/embed/'):
            return parsed.path.split('/', 2)[-1].split('/')[0] or None

        # 4) youtube.com/shorts/<ID>
        if parsed.path.startswith('/shorts/'):
            return parsed.path.split('/', 2)[-1].split('/')[0] or None

        # 5) youtube.com/v/<ID>
        if parsed.path.startswith('/v/'):
            return parsed.path.split('/', 2)[-1].split('/')[0] or None
    return None


def _extract_drive_id(url):
    """يستخرج معرف ملف Google Drive."""
    # /file/d/<ID>/view  أو  open?id=<ID>
    m = re.search(r'/file/d/([A-Za-z0-9_-]+)', url)
    if m:
        return m.group(1)
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        ids = qs.get('id')
        if ids:
            return ids[0]
    except Exception:
        pass
    return None


def _extract_vimeo_id(url):
    m = re.search(r'vimeo\.com/(?:video/)?(\d+)', url)
    return m.group(1) if m else None


@register.filter(name='youtube_embed')
def youtube_embed(url):
    """
    يحوّل الرابط إلى URL قابل للتضمين داخل <iframe>.
    لو لم يستطع التحويل يُرجع الأصلي (قد يعمل أو لا).
    """
    if not url:
        return ''
    s = str(url).strip()
    if not s:
        return ''

    try:
        host = urlparse(s).netloc.lower()
    except Exception:
        return s

    # YouTube
    if any(h in host for h in _YT_HOSTS):
        vid = _extract_youtube_id(s)
        if vid:
            return f'https://www.youtube.com/embed/{vid}?rel=0'
        return s

    # Vimeo
    if any(h in host for h in _VIMEO_HOSTS):
        vid = _extract_vimeo_id(s)
        if vid:
            return f'https://player.vimeo.com/video/{vid}'
        return s

    # Google Drive (preview)
    if any(h in host for h in _DRIVE_HOSTS):
        vid = _extract_drive_id(s)
        if vid:
            return f'https://drive.google.com/file/d/{vid}/preview'
        return s

    # Unknown host — return as-is
    return s


@register.filter(name='cloud_url')
def cloud_url(field_value):
    """يحوّل قيمة CloudinaryField إلى رابط Cloudinary كامل."""
    if not field_value:
        return ''
    # محاولة 1: خاصية .url المدمجة في CloudinaryField
    try:
        url = field_value.url
        if url and url != 'None':
            return url
    except (AttributeError, ValueError):
        pass
    # محاولة 2: تحويل القيمة كنص (public_id)
    val = str(field_value).strip()
    if not val or val == 'None':
        return ''
    if val.startswith('http'):
        return val
    try:
        from cloudinary.utils import cloudinary_url
        url, _ = cloudinary_url(val)
        return url or ''
    except Exception:
        return ''


@register.filter(name='cloud_raw_url')
def cloud_raw_url(field_value):
    """يحوّل قيمة CloudinaryField (resource_type=raw) إلى رابط Cloudinary."""
    if not field_value:
        return ''
    # محاولة 1: خاصية .url المدمجة
    try:
        url = field_value.url
        if url and url != 'None':
            return url
    except (AttributeError, ValueError):
        pass
    # محاولة 2: تحويل public_id إلى رابط raw
    val = str(field_value).strip()
    if not val or val == 'None':
        return ''
    if val.startswith('http'):
        return val
    try:
        from cloudinary.utils import cloudinary_url
        # استخدام signed URL لتجاوز قيود الوصول على raw files
        url, _ = cloudinary_url(val, resource_type='raw', sign_url=True, type='authenticated')
        if url:
            return url
        # محاولة بدون authenticated
        url, _ = cloudinary_url(val, resource_type='raw', sign_url=True)
        return url or ''
    except Exception:
        return ''


@register.filter(name='is_youtube')
def is_youtube(url):
    """يرجع True لو الرابط يوتيوب."""
    if not url:
        return False
    try:
        host = urlparse(str(url)).netloc.lower()
    except Exception:
        return False
    return any(h in host for h in _YT_HOSTS)
