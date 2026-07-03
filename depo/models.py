from django.db import models


class UrunStok(models.Model):
    """
    BZR Market - Ürün Stok Modeli
    
    Her ürünün stok bilgisini, fiyat bilgisini ve kritik eşik değerini tutar.
    En son güncellenen ürün en başta gösterilir.
    """

    # ─── Ürün Bilgileri ───────────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        unique=True,          # Aynı isimde iki ürün olmaz (toplu import için)
        verbose_name="Ürün Adı"
    )
    group = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Grubu",
        help_text="Örn: GIDA, HİJYEN, TEMİZLİK"
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Birim",
        help_text="Örn: Adet, Kilo, Koli vb."
    )

    # ─── Stok Bilgileri ───────────────────────────────────────────────
    stock_quantity = models.IntegerField(
        default=0,
        verbose_name="Stok Miktarı"
    )
    critical_threshold = models.IntegerField(
        default=10,
        verbose_name="Kritik Eşik"
        # Stok bu değerin altına düşünce uyarı verilir
    )

    # ─── Fiyat Bilgileri ──────────────────────────────────────────────
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Alış Fiyatı (₺)"
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Satış Fiyatı (₺)"
    )

    # ─── Tarih/Zaman Bilgileri ────────────────────────────────────────
    created_at = models.DateTimeField(
        auto_now_add=True,    # Sadece ilk kaydedilişte otomatik doldurulur
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,        # Her güncellemede otomatik doldurulur
        verbose_name="Son Güncelleme"
    )

    # ─── Meta Ayarları ────────────────────────────────────────────────
    class Meta:
        ordering = ['-updated_at']        # En son güncellenen ürün önce
        verbose_name = "Ürün Stok"
        verbose_name_plural = "Ürün Stoklar"

    def __str__(self):
        return f"{self.name} (Stok: {self.stock_quantity})"

    # ─── Yardımcı Özellikler (property) ──────────────────────────────
    @property
    def kar(self):
        """Birim başına kâr = Satış Fiyatı - Alış Fiyatı"""
        return self.sale_price - self.purchase_price

    @property
    def kar_orani(self):
        """Kâr oranı yüzdesi (purchase_price sıfır değilse)"""
        if self.purchase_price > 0:
            return round((self.kar / self.purchase_price) * 100, 1)
        return 0

    @property
    def kritik_mi(self):
        """Stok kritik eşiğin altında ya da eşitinde mi?"""
        return self.stock_quantity <= self.critical_threshold
