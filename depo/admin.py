from django.contrib import admin
from .models import UrunStok


@admin.register(UrunStok)
class UrunStokAdmin(admin.ModelAdmin):
    """
    Django Admin panelinde UrunStok yönetimi.
    /admin/ adresinden erişilebilir.
    """
    # Liste sayfasında gösterilecek sütunlar
    list_display = [
        'name', 'stock_quantity', 'critical_threshold',
        'purchase_price', 'sale_price', 'kar', 'kritik_mi',
        'updated_at'
    ]
    
    # Arama kutusu
    search_fields = ['name']
    
    # Sağ taraftaki filtreler
    list_filter = ['created_at', 'updated_at']
    
    # Salt okunur alanlar (formda değiştirilemez)
    readonly_fields = ['created_at', 'updated_at']
    
    # Listedeki sıralama
    ordering = ['-updated_at']
