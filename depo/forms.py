from django import forms
from .models import UrunStok


class UrunStokForm(forms.ModelForm):
    """
    Ürün ekleme ve düzenleme formu.
    Bootstrap 5 CSS sınıfları otomatik uygulanır.
    """

    class Meta:
        model = UrunStok
        # Formda gösterilecek alanlar (created_at ve updated_at otomatik)
        fields = ['name', 'group', 'unit', 'stock_quantity', 'critical_threshold',
                  'purchase_price', 'sale_price']

        # Her alan için Bootstrap 'form-control' sınıfı ve Türkçe etiketler
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Çikolatalı Kek 500g'
            }),
            'group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: GIDA, HİJYEN'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Adet, Kilo, Paket'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'critical_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }

        labels = {
            'name': 'Ürün Adı',
            'group': 'Grubu',
            'unit': 'Birim',
            'stock_quantity': 'Stok Miktarı',
            'critical_threshold': 'Kritik Eşik Değeri',
            'purchase_price': 'Alış Fiyatı (₺)',
            'sale_price': 'Satış Fiyatı (₺)',
        }

        help_texts = {
            'critical_threshold': 'Stok bu değerin altına düştüğünde uyarı verilir.',
            'name': 'Ürün adı benzersiz olmalıdır (aynı isimde iki ürün olamaz).',
        }

    def clean(self):
        """
        Fiyat doğrulama: Satış fiyatı alış fiyatından düşük olmamalı.
        (Uyarı verir, engel koymaz - isteğe bağlı değiştirilebilir)
        """
        cleaned_data = super().clean()
        purchase = cleaned_data.get('purchase_price')
        sale = cleaned_data.get('sale_price')

        if purchase and sale and sale < purchase:
            self.add_error('sale_price',
                '⚠️ Satış fiyatı alış fiyatından düşük! Zarar edersiniz.')
        return cleaned_data


class BulkImportForm(forms.Form):
    """
    Excel (.xlsx) veya CSV (.csv) dosyası yüklemek için form.
    Toplu ürün ekleme/güncelleme işleminde kullanılır.
    """
    dosya = forms.FileField(
        label='Excel veya CSV Dosyası',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'  # Tarayıcı sadece bu dosyaları önerir
        }),
        help_text='Desteklenen formatlar: .xlsx, .xls, .csv | '
                  'Sütunlar: name, stock_quantity, critical_threshold, '
                  'purchase_price, sale_price'
    )
