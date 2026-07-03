<div align="center">
  <h1 align="center">📦 BZR Stok Yönetim Sistemi</h1>
  <p align="center">
    <strong>Gelişmiş, kullanımı kolay ve güvenilir bir stok takip ve yönetim sistemi.</strong>
  </p>
</div>

## 📝 Hakkında
**BZR Stok**, ürün stok durumlarını, kritik eşik seviyelerini ve kar-zarar oranlarını etkili bir şekilde takip edebilmenizi sağlayan Django tabanlı bir web uygulamasıdır. 

## 🚀 Özellikler
- **Ürün Yönetimi:** Ürünlerinizi birim ve grup bazında detaylıca sisteme ekleyebilirsiniz.
- **Kritik Stok Uyarısı:** Stoklarınız belirlediğiniz eşiğin altına düştüğünde sistem size anlık olarak uyarı verebilir.
- **Karlılık Analizi:** Ürünlerin alış ve satış fiyatları üzerinden otomatik kar ve kar oranı yüzdesi hesaplamaları yapar.
- **Kolay Takip:** En son güncellenen ürünleri listeleyerek stok hareketlerinizi hızla izleme imkanı sunar.

## 💻 Teknoloji Yığını
- **Backend:** Python, Django
- **Veritabanı:** SQLite (Geliştirme Ortamı)

## 🛠️ Kurulum
Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

```bash
# Repoyu klonlayın
git clone https://github.com/omernazroglu/BZR_Stok.git

# Proje dizinine girin
cd BZR_Stok

# Gerekli bağımlılıkları yükleyin
pip install -r requirements.txt

# Veritabanı tablolarını oluşturun
python manage.py migrate

# Sunucuyu başlatın
python manage.py runserver
```

## 👨‍💻 Geliştirici
- [Ömer Nazıroğlu](https://github.com/omernazroglu)
