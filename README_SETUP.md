# EduPace Setup Instructions

## Yeni Özellikler İçin Gerekli Adımlar

### 1. Migration'ları Uygulayın
Projeyi çektikten sonra mutlaka migration'ları çalıştırın:

```bash
python manage.py migrate
```

Bu komut veritabanını güncelleyecek ve yeni özellikler için gerekli tabloları/alanları ekleyecektir.

### 2. Önemli Notlar

#### Assessment Type Özelliği
- Grade modeline `assessment_type` alanı eklendi
- Migration: `0003_add_assessment_type_to_grade.py`
- Bu migration'ı mutlaka uygulayın, aksi takdirde grade ekleme çalışmaz

#### Context Processor
- Navbar'da role gösterimi için `context_processors.py` eklendi
- `settings.py`'da context processor kayıtlı
- Eğer navbar'da role görünmüyorsa, `settings.py` dosyasını kontrol edin

### 3. Hızlı Kurulum

```bash
# 1. Projeyi klonlayın veya pull edin
git pull origin development

# 2. Migration'ları uygulayın (ÇOK ÖNEMLİ!)
python manage.py migrate

# 3. Sunucuyu başlatın
python manage.py runserver
```

### 4. Sık Karşılaşılan Sorunlar

#### Sorun: Grade eklerken hata alıyorum
**Çözüm:** Migration'ları uygulayın:
```bash
python manage.py migrate
```

#### Sorun: Navbar'da role görünmüyor
**Çözüm:** `Eduu_Pace/settings.py` dosyasında şu satırın olduğundan emin olun:
```python
"edupace_app.context_processors.user_role_context",
```
Context processors listesinde olmalı.

#### Sorun: Assessment type field'ı görünmüyor
**Çözüm:** Migration'ları uygulayın ve sayfayı yenileyin.

### 5. Veritabanı Sıfırlama (Gerekirse)

Eğer sorunlar devam ederse:

```bash
# DİKKAT: Bu işlem tüm verileri siler!
# Sadece development ortamında kullanın

# Migration dosyalarını sil (migrations klasöründen 0003_*.py hariç)
# Sonra:
python manage.py migrate
```

### 6. Güncel Migration Listesi

- `0001_initial` - İlk migration
- `0002_add_assessment_models` - Assessment modelleri
- `0003_add_assessment_type_to_grade` - Assessment type alanı

### 7. Test

Projeyi çalıştırdıktan sonra test edin:
- Login yapabilmeli
- Grade ekleyebilmeli (assessment type seçebilmeli)
- Navbar'da role görünmeli (Department Head, Teacher, Student)

