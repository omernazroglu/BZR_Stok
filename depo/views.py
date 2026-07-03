"""
BZR Stok Yönetim Sistemi - Views (Görünümler)
=============================================
Her view fonksiyonunun üstünde ne yaptığı detaylı açıklanmıştır.
"""

import csv
import io

import pandas as pd
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BulkImportForm, UrunStokForm
from .models import UrunStok


# ══════════════════════════════════════════════════════════════════════
#  1. DASHBOARD - Ana Sayfa / Ürün Listesi
# ══════════════════════════════════════════════════════════════════════

def dashboard(request):
    """
    Ana kontrol paneli.
    
    GET ?q=... → arama filtresi
    """
    from django.db.models import F, ExpressionWrapper, DecimalField, Sum

    arama = request.GET.get('q', '').strip()
    urunler = UrunStok.objects.all()

    if arama:
        urunler = urunler.filter(name__icontains=arama)

    # Kritik ürün sayısı: stock_quantity <= critical_threshold
    # Django'da iki alan karşılaştırması için F() kullanılır
    kritik_sayisi = UrunStok.objects.filter(
        stock_quantity__lte=F('critical_threshold')
    ).count()

    toplam_urun = UrunStok.objects.count()

    # Toplam stok değeri = Σ (stok_miktarı × alış_fiyatı)
    # aggregate ile tek sorguda hesaplanır (verimli)
    toplam_deger_qs = UrunStok.objects.aggregate(
        toplam=Sum(
            ExpressionWrapper(
                F('stock_quantity') * F('purchase_price'),
                output_field=DecimalField()
            )
        )
    )
    toplam_deger = toplam_deger_qs['toplam'] or 0

    context = {
        'urunler': urunler,
        'arama': arama,
        'toplam_urun': toplam_urun,
        'kritik_sayisi': kritik_sayisi,
        'toplam_deger': round(toplam_deger, 2),
        'sayfa_basligi': 'Dashboard',
    }
    return render(request, 'depo/dashboard.html', context)


# ══════════════════════════════════════════════════════════════════════
#  2. CRUD - Ürün Ekleme
# ══════════════════════════════════════════════════════════════════════

def urun_ekle(request):
    """
    Yeni ürün ekleme sayfası.
    
    GET  → Boş formu göster
    POST → Formu doğrula ve kaydet
    """
    if request.method == 'POST':
        form = UrunStokForm(request.POST)
        if form.is_valid():
            urun = form.save()
            # Başarı mesajı - Django messages framework kullanır
            messages.success(
                request,
                f'✅ "{urun.name}" başarıyla eklendi!'
            )
            return redirect('depo:dashboard')
        else:
            # Hata varsa formu hata mesajlarıyla birlikte tekrar göster
            messages.error(request, '❌ Lütfen formdaki hataları düzeltin.')
    else:
        form = UrunStokForm()  # GET isteğinde boş form

    return render(request, 'depo/urun_form.html', {
        'form': form,
        'sayfa_basligi': 'Yeni Ürün Ekle',
        'buton_metni': 'Ürün Ekle',
        'islem': 'ekle',
    })


# ══════════════════════════════════════════════════════════════════════
#  3. CRUD - Ürün Düzenleme
# ══════════════════════════════════════════════════════════════════════

def urun_duzenle(request, pk):
    """
    Mevcut ürünü düzenleme sayfası.
    
    pk  → Düzenlenecek ürünün birincil anahtarı (ID'si)
    GET  → Mevcut verileri dolu formda göster
    POST → Güncellenmiş formu doğrula ve kaydet
    """
    # get_object_or_404: Ürün yoksa otomatik 404 hatası döner
    urun = get_object_or_404(UrunStok, pk=pk)

    if request.method == 'POST':
        # instance=urun → Yeni kayıt değil, mevcut kaydı güncelle
        form = UrunStokForm(request.POST, instance=urun)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'✅ "{urun.name}" başarıyla güncellendi!'
            )
            return redirect('depo:dashboard')
        else:
            messages.error(request, '❌ Lütfen formdaki hataları düzeltin.')
    else:
        # GET isteğinde: mevcut ürün verilerini forma doldur
        form = UrunStokForm(instance=urun)

    return render(request, 'depo/urun_form.html', {
        'form': form,
        'urun': urun,
        'sayfa_basligi': f'Düzenle: {urun.name}',
        'buton_metni': 'Güncelle',
        'islem': 'duzenle',
    })


# ══════════════════════════════════════════════════════════════════════
#  4. CRUD - Ürün Silme
# ══════════════════════════════════════════════════════════════════════

def urun_sil(request, pk):
    """
    Ürün silme sayfası.
    
    GET  → Silme onay sayfasını göster
    POST → Ürünü sil ve dashboard'a dön
    """
    urun = get_object_or_404(UrunStok, pk=pk)

    if request.method == 'POST':
        isim = urun.name  # Silmeden önce ismi sakla (mesaj için)
        urun.delete()
        messages.success(request, f'🗑️ "{isim}" başarıyla silindi.')
        return redirect('depo:dashboard')

    return render(request, 'depo/urun_sil.html', {
        'urun': urun,
        'sayfa_basligi': f'Sil: {urun.name}',
    })


# ══════════════════════════════════════════════════════════════════════
#  5. HIZLI STOK GÜNCELLEME (+1 / -1) - AJAX
# ══════════════════════════════════════════════════════════════════════

@require_POST  # Sadece POST isteği kabul et (güvenlik)
def stok_guncelle(request, pk, islem):
    """
    Dashboard'daki +1 / -1 butonlarına cevap verir.
    Sayfa yenilenmeden AJAX ile stok güncellenir.
    
    pk    → Ürün ID'si
    islem → 'artir' veya 'azalt'
    
    JSON döner: {"yeni_stok": 15, "kritik_mi": false}
    """
    urun = get_object_or_404(UrunStok, pk=pk)

    if islem == 'artir':
        urun.stock_quantity += 1
    elif islem == 'azalt':
        # Stok 0'ın altına düşmesin
        if urun.stock_quantity > 0:
            urun.stock_quantity -= 1
        else:
            return JsonResponse({
                'hata': 'Stok zaten 0, daha fazla azaltılamaz.',
                'yeni_stok': 0,
                'kritik_mi': urun.kritik_mi,
            }, status=400)
    else:
        return JsonResponse({'hata': 'Geçersiz işlem.'}, status=400)

    # Sadece stock_quantity alanını kaydet (update_fields ile verimli)
    urun.save(update_fields=['stock_quantity', 'updated_at'])

    from django.db.models import F, ExpressionWrapper, DecimalField, Sum
    toplam_deger_qs = UrunStok.objects.aggregate(
        toplam=Sum(
            ExpressionWrapper(
                F('stock_quantity') * F('purchase_price'),
                output_field=DecimalField()
            )
        )
    )
    toplam_deger = toplam_deger_qs['toplam'] or 0

    return JsonResponse({
        'yeni_stok': urun.stock_quantity,
        'kritik_mi': urun.kritik_mi,
        'toplam_deger': f"{toplam_deger:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # TR format
    })

# ══════════════════════════════════════════════════════════════════════
#  HIZLI FİYAT DEĞİŞTİRME API'LERİ
# ══════════════════════════════════════════════════════════════════════
from django.db.models import Q
import json

def api_urun_ara(request):
    """
    Hızlı Fiyat Değiştirme Modalı için ürün arama endpointi.
    """
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'sonuclar': []})
        
    urunler = UrunStok.objects.filter(name__icontains=q)[:10]
    sonuclar = [{
        'id': u.pk,
        'text': f"{u.name} (Alış: {u.purchase_price} ₺, Satış: {u.sale_price} ₺)",
        'purchase_price': float(u.purchase_price),
        'sale_price': float(u.sale_price)
    } for u in urunler]
    
    return JsonResponse({'sonuclar': sonuclar})

@require_POST
def api_fiyat_guncelle(request):
    """
    Seçilen ürünün fiyatlarını günceller.
    """
    try:
        data = json.loads(request.body)
        urun_id = data.get('urun_id')
        yeni_alis = float(data.get('purchase_price', 0))
        yeni_satis = float(data.get('sale_price', 0))
        
        urun = get_object_or_404(UrunStok, pk=urun_id)
        urun.purchase_price = yeni_alis
        urun.sale_price = yeni_satis
        urun.save(update_fields=['purchase_price', 'sale_price', 'updated_at'])
        
        return JsonResponse({'success': True, 'mesaj': 'Fiyatlar başarıyla güncellendi!'})
    except Exception as e:
        return JsonResponse({'success': False, 'hata': str(e)}, status=400)

@require_POST
def api_toplu_sil(request):
    """
    Dashboard üzerinden seçili ürünleri topluca siler.
    Beklenen JSON: {"urun_idleri": [1, 2, 5]}
    """
    try:
        data = json.loads(request.body)
        urun_idleri = data.get('urun_idleri', [])
        
        if not urun_idleri:
            return JsonResponse({'success': False, 'hata': 'Silinecek ürün seçilmedi.'}, status=400)
            
        silinen_sayisi, _ = UrunStok.objects.filter(pk__in=urun_idleri).delete()
        
        return JsonResponse({'success': True, 'mesaj': f'{silinen_sayisi} adet ürün başarıyla silindi.'})
    except Exception as e:
        return JsonResponse({'success': False, 'hata': str(e)}, status=400)


# ══════════════════════════════════════════════════════════════════════
#  6. TOPLU İÇE AKTARMA - Excel / CSV
# ══════════════════════════════════════════════════════════════════════

def bulk_import(request):
    """
    Excel (.xlsx/.xls) veya CSV (.csv) dosyasından toplu ürün içe aktarır.
    
    Mantık:
    - Dosyayı pandas ile oku
    - Her satır için: ürün adına göre bak
      - Varsa → güncelle (UPDATE)
      - Yoksa → yeni ekle (INSERT)
    - Bu işleme 'upsert' denir
    
    Beklenen sütunlar (zorunlu):
        name, stock_quantity, critical_threshold, purchase_price, sale_price
    """
    form = BulkImportForm()

    if request.method == 'POST':
        form = BulkImportForm(request.POST, request.FILES)

        if form.is_valid():
            dosya = request.FILES['dosya']
            dosya_adi = dosya.name.lower()

            try:
                # ── Dosya türüne göre pandas ile oku ──────────────────
                if dosya_adi.endswith('.csv'):
                    # CSV için: UTF-8 veya Latin-1 dene
                    try:
                        icerik = dosya.read().decode('utf-8')
                    except UnicodeDecodeError:
                        icerik = dosya.read().decode('latin-1')
                    df = pd.read_csv(io.StringIO(icerik))

                elif dosya_adi.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(dosya)
                else:
                    messages.error(request,
                        '❌ Desteklenmeyen dosya türü. Sadece .csv, .xlsx, .xls')
                    return render(request, 'depo/bulk_import.html',
                                  {'form': form, 'sayfa_basligi': 'Toplu İçe Aktar'})

                # ── Sütun adlarını temizle (boşluk, büyük/küçük) ──────
                df.columns = df.columns.str.strip().str.lower()

                # ── Sütun Eşleştirmesi (Kullanıcının Excel Formatı) ───
                rename_mapping = {
                    'stok adı / grubu': 'name',
                    'stok adı': 'name',
                    'alış fiyatı 1': 'purchase_price',
                    'satış fiyatı 1': 'sale_price',
                    'birim': 'unit',
                    'grubu': 'group'
                }
                df.rename(columns=rename_mapping, inplace=True)

                # ── Zorunlu sütunları kontrol et ──────────────────────
                # Artık sadece isim ve fiyatlar zorunlu, stok dosyada yok.
                zorunlu = {'name', 'purchase_price', 'sale_price'}
                eksik = zorunlu - set(df.columns)
                if eksik:
                    messages.error(request,
                        f'❌ Dosyada eksik sütunlar var (Stok Adı, Alış Fiyatı 1, Satış Fiyatı 1 olmalı): {", ".join(eksik)}')
                    return render(request, 'depo/bulk_import.html',
                                  {'form': form, 'sayfa_basligi': 'Toplu İçe Aktar'})

                # ── Boş satırları at ──────────────────────────────────
                df = df.dropna(subset=['name'])

                # ── Satırları tek tek işle (upsert) ───────────────────
                eklenen = 0
                guncellenen = 0
                hatali = 0

                for index, satir in df.iterrows():
                    try:
                        urun_adi = str(satir['name']).strip()

                        # İsimlerin sonundaki PDF ibaresini (büyük/küçük harf fark etmeksizin) temizle
                        if urun_adi.lower().endswith(' pdf'):
                            urun_adi = urun_adi[:-4].strip()
                        elif urun_adi.lower().endswith('pdf'):
                            urun_adi = urun_adi[:-3].strip()

                        if not urun_adi:
                            continue

                        # Fiyatlardaki virgülü noktaya çevir (Örn: "113,64" -> "113.64")
                        def parse_price(val):
                            if pd.isna(val):
                                return 0.0
                            if isinstance(val, str):
                                # Varsa binlik ayracını (nokta) sil, virgülü noktaya çevir
                                val = val.replace('.', '').replace(',', '.')
                            return float(val)

                        p_price = parse_price(satir.get('purchase_price', 0))
                        s_price = parse_price(satir.get('sale_price', 0))
                        urun_birimi = str(satir.get('unit', '')).strip() if pd.notna(satir.get('unit')) else ''
                        urun_grubu = str(satir.get('group', '')).strip() if pd.notna(satir.get('group')) else ''

                        # update_or_create:
                        # - defaults → bu alanları güncelle/ekle
                        # - Mevcut stoğu ezmemek için 'stock_quantity' eklemiyoruz (yeni ise default 0 olur)
                        urun, yeni_mi = UrunStok.objects.update_or_create(
                            name=urun_adi,
                            defaults={
                                'purchase_price': p_price,
                                'sale_price': s_price,
                                'unit': urun_birimi,
                                'group': urun_grubu,
                                'critical_threshold': 2,  # Otomatik 2 atanır
                            }
                        )

                        if yeni_mi:
                            eklenen += 1
                        else:
                            guncellenen += 1

                    except Exception as satir_hatasi:
                        hatali += 1
                        # Hatalı satırı atla, diğerlerine devam et
                        continue

                # ── Sonuç mesajları ───────────────────────────────────
                if eklenen > 0:
                    messages.success(request,
                        f'✅ {eklenen} yeni ürün eklendi.')
                if guncellenen > 0:
                    messages.info(request,
                        f'🔄 {guncellenen} mevcut ürün güncellendi.')
                if hatali > 0:
                    messages.warning(request,
                        f'⚠️ {hatali} satır işlenemedi (hatalı veri).')

                return redirect('depo:dashboard')

            except Exception as e:
                messages.error(request,
                    f'❌ Dosya okunurken hata oluştu: {str(e)}')

    return render(request, 'depo/bulk_import.html', {
        'form': form,
        'sayfa_basligi': 'Toplu İçe Aktarma',
    })


# ══════════════════════════════════════════════════════════════════════
#  7. RAPORLAR - Kritik Stok Uyarıları
# ══════════════════════════════════════════════════════════════════════

def raporlar(request):
    """
    Raporlar sayfası.
    
    - Kritik stok listesi (stock_quantity <= critical_threshold)
    - Kâr marjı listesi (yüksekten düşüğe)
    - Özet istatistikler
    
    Django ORM'de iki alan karşılaştırması için F() kullanılır.
    """
    from django.db.models import F, ExpressionWrapper, DecimalField, Sum, Avg

    # Kritik stoktaki ürünler: stok_miktarı <= kritik_eşik
    kritik_urunler = UrunStok.objects.filter(
        stock_quantity__lte=F('critical_threshold')
    ).order_by('stock_quantity')  # En az stoklu önde

    # Kâr analizine göre tüm ürünler (sale_price yüksekten düşüğe)
    kar_listesi = UrunStok.objects.all().order_by(
        '-sale_price'  # Satış fiyatına göre sırala
    )

    # Özet istatistikler (aggregate → tek SQL sorgusu, verimli)
    ozet = UrunStok.objects.aggregate(
        toplam_urun=Sum('stock_quantity'),
        ort_kar=Avg(
            ExpressionWrapper(
                F('sale_price') - F('purchase_price'),
                output_field=DecimalField()
            )
        ),
        toplam_stok_degeri=Sum(
            ExpressionWrapper(
                F('stock_quantity') * F('purchase_price'),
                output_field=DecimalField()
            )
        ),
    )

    context = {
        'kritik_urunler': kritik_urunler,
        'kar_listesi': kar_listesi,
        'kritik_sayisi': kritik_urunler.count(),
        'ozet': ozet,
        'sayfa_basligi': 'Raporlar & Uyarılar',
    }
    return render(request, 'depo/raporlar.html', context)
