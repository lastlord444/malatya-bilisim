# Malatya Bilişim AI Reels Factory (`malatya-bilisim`)

Malatya Bilişim (@malatyabilisim44) Instagram hesabı için profesyonel, dikey (9:16) Reels içerik üretim, doğrulama, insan onayı, otomatik Gemini indirmesi ve Upload-Post yayın boru hattı.

Bu depo her ortamdan (yerel geliştirme, başka bilgisayarlar, Box VPS veya bulut sunucuları) erişilebilir ve birden fazla Google/Gemini hesabı ile çalışabilecek şekilde modüler olarak tasarlanmıştır.

---

## 🚀 Proje Yapısı

```text
malatya-bilisim/
│
├── config/
│   ├── brand.json            # Marka stratejisi, renk kodları (#0B1020, #2DE2E6, #F4F7FA), 4 ana hizmet
│   └── pipeline.json         # Boru hattı ayarları, API uç noktaları, güvenlik eşikleri
│
├── prompts/
│   ├── creative-director.txt # Gemini Kreatif Direktör talimatları ve bağlam koruma kuralları
│   └── video-generation.txt  # Dikey (9:16) video modelleri (Veo, Wan, LTX) için prompt şablonu
│
├── src/
│   ├── account_manager.py    # Çoklu Google / Gemini hesabı algılama ve yönlendirme yöneticisi
│   ├── gemini_downloader.py  # Gemini resmî butonundan inen MP4'leri otomatik yakalama ve doğrulama
│   ├── video_checker.py      # MP4 teknik kontrolü (çözünürlük, 9:16 oranı, süre, codec, ses)
│   ├── upload_post.py        # Upload-Post REST API adaptörü (multipart/form-data yerel MP4 desteği)
│   ├── approval.py           # İnsan onayı ve mükerrer yayın koruma yöneticisi (SHA-256)
│   └── pipeline.py           # Boru hattı orkestratörü (bağlam yönetimi, kayıt, doğrulama, yayın)
│
├── notebooks/
│   └── colab_gpu_test.ipynb  # Colab GPU ve model uygunluk (LTX-Video, Wan 2.1) test defteri
│
├── data/
│   ├── reels_history.json    # Son 30 içeriğin hafif JSON geçmişi (bağlam şişmesini önler)
│   ├── gemini_reel_9x16.mp4  # 720x1280 9:16 Dikey, H.264/AAC doğrulanmış gerçek Gemini Veo videosu
│   └── sample_reel.mp4       # 1080x1920 8s H.264 / AAC doğrulanmış test videosu
│
├── tests/
│   ├── test_account_manager.py   # Çoklu hesap yönetimi testleri
│   ├── test_gemini_downloader.py # Otomatik indirme testleri
│   ├── test_video_checker.py     # Video teknik doğrulama testleri
│   ├── test_upload_post.py       # Yayın adaptörü ve güvenlik bariyeri testleri
│   └── test_approval.py          # İnsan onayı ve dosya bütünlüğü hash testleri
│
├── screenshots/              # Tarayıcı üzerinden doğrulanan hesap ve sistem kanıtları
├── .env.example              # Ortam değişkenleri şablonu (çoklu hesap destekli)
├── .gitignore                # Güvenlik kuralları (API anahtarları depoya asla girmez)
├── README.md
└── SETUP_REPORT.md           # Kapsamlı Faz 1 & Faz 2 kurulum, araştırma ve durum raporu
```

---

## 👥 Farklı Gemini Hesaplarına Yönlendirme (Multi-Account Setup)

Sistem tek bir Google hesabına bağımlı değildir. Farklı bir Google/Gemini hesabı ile çalışmak için iki pratik yöntem bulunur:

### 1. `.env` Üzerinden Hesap İndeksi Belirleme:
Google Chrome üzerinde birden fazla Google hesabı açıksa:
- Varsayılan / 1. Hesap: `GEMINI_ACCOUNT_INDEX="0"` -> `https://gemini.google.com/app`
- 2. Hesap: `GEMINI_ACCOUNT_INDEX="1"` -> `https://gemini.google.com/u/1/app`
- 3. Hesap: `GEMINI_ACCOUNT_INDEX="2"` -> `https://gemini.google.com/u/2/app`

Ayrıca belirli bir e-posta hedeflenmek istenirse:
```bash
GEMINI_TARGET_EMAIL="yeni_hesap@gmail.com"
```

### 2. Python Kodu ile Dinamik Hesap Yönlendirme:
```python
from src.account_manager import GeminiAccountManager

account_mgr = GeminiAccountManager(target_account_index=1)
url = account_mgr.get_gemini_url() # https://gemini.google.com/u/1/app
```

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/lastlord444/malatya-bilisim.git
cd malatya-bilisim
```

### 2. Ortam Değişkenlerini Ayarlayın
`.env.example` dosyasını `.env` olarak kopyalayın:
```bash
copy .env.example .env
```

### 3. Bağımlılıklar
- Python 3.10+
- `pip install requests python-dotenv`
- `ffmpeg` / `ffprobe` (Windows: `winget install Gyan.FFmpeg`, Linux: `sudo apt install ffmpeg`)

### 4. Bütün Testleri Çalıştırma
```bash
python -m unittest discover -s tests -p "test_*.py"
```
*(14 testin tamamı otomatik olarak çalışır ve doğrulanır)*

### 5. Boru Hattı Akışı
```python
from src.pipeline import ReelsPipeline

pipeline = ReelsPipeline()

# 1. Günlük temiz bağlamı al (bağlam şişmesini engeller)
context = pipeline.get_clean_daily_context()

# 2. Gemini'den inen en son videoyu içeri al ve doğrula
ingest = pipeline.ingest_gemini_video()

# 3. İnsan onayını kaydet
pipeline.approve_reel("REEL-2026-002", ingest["dest_path"], "Instagram Açıklaması", approver="Yönetici")

# 4. Güvenli yayını başlat (Öncelikle dry_run=True ile test edin)
result = pipeline.publish_reel("REEL-2026-002", ingest["dest_path"], "Instagram Açıklaması", dry_run=True)
```
