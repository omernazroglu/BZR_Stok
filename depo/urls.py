"""
BZR Stok - URL Yönlendirmeleri (depo uygulaması)
=================================================
Tüm URL'ler 'depo' namespace'i altında tanımlanmıştır.
Template'lerde {% url 'depo:dashboard' %} şeklinde kullanılır.
"""

from django.urls import path
from . import views

# Namespace: Template'lerde 'depo:view_adi' şeklinde kullanılır
app_name = 'depo'

urlpatterns = [
    # ── Ana Sayfa / Dashboard ─────────────────────────────────────────
    # URL: /depo/
    path('', views.dashboard, name='dashboard'),

    # ── Ürün Ekleme ───────────────────────────────────────────────────
    # URL: /depo/ekle/
    path('ekle/', views.urun_ekle, name='urun_ekle'),

    # ── Ürün Düzenleme ────────────────────────────────────────────────
    # URL: /depo/duzenle/5/  (5 = ürün ID'si)
    # <int:pk> → Django otomatik integer'a çevirir ve view'e gönderir
    path('duzenle/<int:pk>/', views.urun_duzenle, name='urun_duzenle'),

    # ── Ürün Silme ────────────────────────────────────────────────────
    # URL: /depo/sil/5/
    path('sil/<int:pk>/', views.urun_sil, name='urun_sil'),

    # ── Hızlı Stok Güncelleme (AJAX) ─────────────────────────────────
    # URL: /depo/stok/5/artir/  veya  /depo/stok/5/azalt/
    # <str:islem> → 'artir' veya 'azalt' değerini alır
    path('stok/<int:pk>/<str:islem>/', views.stok_guncelle, name='stok_guncelle'),

    # ── Toplu İçe Aktarma ─────────────────────────────────────────────
    # URL: /depo/import/
    path('import/', views.bulk_import, name='bulk_import'),

    # ── Raporlar ──────────────────────────────────────────────────────
    # URL: /depo/raporlar/
    path('raporlar/', views.raporlar, name='raporlar'),

    # ── Hızlı Fiyat Değiştirme API'leri ──────────────────────────────
    path('api/ara/', views.api_urun_ara, name='api_urun_ara'),
    path('api/fiyat-guncelle/', views.api_fiyat_guncelle, name='api_fiyat_guncelle'),
    path('api/toplu-sil/', views.api_toplu_sil, name='api_toplu_sil'),
    
    path('api/urunler/', views.stok_urun_listesi_api, name='stok_urun_listesi_api'),
]
