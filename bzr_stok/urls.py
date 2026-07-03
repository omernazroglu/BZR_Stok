"""
URL yapılandırması - bzr_stok projesi
=====================================
Ana URL dosyası.
/         → depo uygulamasına yönlendir (dashboard)
/depo/    → depo uygulamasının tüm URL'leri
/admin/   → Django yönetim paneli
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def anasayfa_yonlendir(request):
    """Kök URL'yi (/), depo dashboard'una yönlendirir."""
    return redirect('depo:dashboard')


urlpatterns = [
    # ── Django Admin ──────────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Kök URL → Dashboard'a yönlendirme ────────────────────────────
    # Kullanıcı http://127.0.0.1:8000/ açınca direkt dashboard'a gider
    path('', anasayfa_yonlendir),

    # ── Depo Uygulaması ───────────────────────────────────────────────
    # depo/urls.py'deki tüm URL'leri /depo/ öneki ile ekle
    # namespace='depo' → template'lerde {% url 'depo:dashboard' %} kullanılır
    path('depo/', include('depo.urls', namespace='depo')),
]

# Development ortamında medya dosyalarını sun
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
