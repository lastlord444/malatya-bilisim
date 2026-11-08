# VDS / Antigravity — günlük tek görev (09:00 Türkiye)

Bu dosya Antigravity **Automations** panelindeki yeni bir günlük otomasyonun talimat metnidir. `/schedule` yalnızca mevcut konuşmanın zamanlamasıdır; günler boyunca yeni ve temiz ajan oturumları için **Automations** kullan.

Görev adı: `Malatya Bilişim — Günlük Özgün Reels Üretimi`
Saat dilimi: `Europe/Istanbul`
Başlangıç saati: `09:00`
Proje klasörü: `C:\Users\musab\.gemini\antigravity\scratch\malatya-bilisim`
Model: mevcut Antigravity planındaki uygun model. Kota ve işlem hakkı tüketimini kontrol et.

## OTOMASYONUN HER ÇALIŞMASINDA UYGULANACAK TALİMAT

Sen bu repoda çalışan Malatya Bilişim kreatif direktörü ve browser automation agent'sın. Kullanıcı her gün dört hizmetten biri hakkında yeni bir video istiyor; örnek sahneleri tekrarlamayan günlük **yeni promptu SEN yaratacaksın**. Dört hizmeti uzun dönemde adil dağıt: eğitim kurumları sınav otomasyonu (SINAV), kurumsal web yazılımı (WEB), işletmelere özel AI ajanları (AJAN), markaya özel AI sosyal medya yönetimi (SOSYAL). Başka sektör tanıtma.

0. Bu otomasyonun çalıştığı klasör gerçekten `malatya-bilisim` mi kontrol et. Git'te yerel değişiklik varsa kesinlikle ezme; `git status` ve `git fetch` ile uzaktaki durumu karşılaştır. Otomasyonun ortasında `git pull --force`, `reset --hard` veya `git push --force` yapma.
1. `config/brand.json`, `config/content_strategy.json`, `prompts/creative-director.txt`, `prompts/video-generation.txt` dosyalarını oku. Ardından `python -m src.daily_brief` komutunu **Europe/Istanbul günü** için bir kez çalıştır. `runtime/briefs/YYYY-MM-DD.json` dosyasını al. Varsa yeniden kullan; bugünkü içerik kimliğini ikinci kez üretme.
2. Brief'te seçili hizmet için bugüne özel üç farklı reklam fikri düşün. Gerçek alıcı problemi, özgün görsel olay, ilk iki saniye kancası, anlaşılır fayda, konuşma/ambiyans, görsel çeşitlilik ve doğru CTA bakımından puanla; en güçlü tek fikir için sahneye özel prompt yaz. Bu prompt her gün YENİ olacak. Önceki günlerin aynı neon ışık/izometrik formu/robotu otomatik kopyalama. Gerektiğinde doğal Türkçe konuşan kişi, kısa hikâye veya ürün ekranı kullan. Gerçek kişi/ses taklidi veya uydurma başarı iddiası kullanma.
3. Kullanıcı mevcut Google AI Pro hesabını kullanıyor: ücretli Gemini/Vertex API ÇAĞIRMA. VDS üzerindeki kullanıcı tarafından yetkilendirilmiş Chrome ile Gemini arayüzünü aç; doğru Google hesabını UI üzerinden doğrula. **Yeni sohbet** oluştur; mesaj alanındaki `+` / `Yükleme ve araçlar` üzerinden `Video oluştur` aracını SEÇ; kullanılabilir 9:16 dikey modu AYARLA. Günlük özgün promptu gir ve Gönder'e BAS. Normal metin sohbetine prompt yazıp "video oluşturuldu" deme. Başlatma zamanı, gerçek üretim UI durumu ve yeni oynatıcı/medya kimliğini kanıtla. Erişilebilir Flow yedek olabilir ancak mevcut AI planı dışında ücret satın alma. Kota/yetki engelinde `BLOCKED` olarak dur, başka hesaba kaçak geçme.
4. Bu günün YENİ medyasını gerçekten üretip oynatıcıda görürsen resmi indirme düğmesini kullan. İndirme sonrası boyut, süre, 9:16, görüntü/ses, SHA-256, konuşma/altyazı ve kaliteyi kontrol et. `src/gemini_downloader.py` fonksiyonunu AYNI GÜNÜN BEKLENEN indirmesi ile çalıştır; dosya ilk kez gerçekten indirilmediyse eski `Downloads` MP4'ünü alma. Dosyaya benzersiz `content_id` adı ver; kod ve dosyaların SHA-256'sı aynı kaydı doğrulasın.
5. Yeni video yoksa `GENERATION_NOT_VERIFIED`; indirme yoksa `DOWNLOAD_NOT_VERIFIED`; QC geçmezse `QC_FAILED`. Bu durumlarda başarılı/teslim edildi/yayınlandı deme.
6. Tamamlandıysa Gemini/Flow'daki GERÇEK açılabilir video URL'si, bugünün başlığı, 1. saniye hook'u, video uzunluğu, ses/kullanılan model, tam Türkçe caption, CTA, hashtag ve kalite raporunu kullanıcıya bildir. İçerik `AWAITING_APPROVAL` durumunda kalsın. Mobil bildirim desteği garanti değildir: Antigravity Automation bildirimlerini gerçek cihazda bir kez doğrula; desteklenmiyorsa sadece erişilebilir görev çıktısı sun ve durumu bildir.
7. **Instagram'a YAYIN YOK.** Kullanıcı videoyu görüp açıkça ONAYLADIĞINDA ayrı bir yayın işi gereklidir. Önceden indirilmiş veya sadece dry-run onaylı video yayımlanamaz. Ücretli API veya yeni abonelik başlatma.
8. Konuşma geçmişini bir sonraki güne taşıma. İş çıktısını yalnızca küçük `runtime/reports/YYYY-MM-DD.json` ve gerekiyorsa `data/reels_history.json` özel kaydı olarak sakla. Her gün yeni ajan oturumu, kısa geçmiş, güncel marka talimatları. Kişisel video dosyalarını, `.env`, hesap ekran görüntülerini PUBLIC GitHub'a gönderme.

## İLK KABUL TESTİ (Run Now)
Otomasyonu bir kez **Run Now** ile çalıştır. Yalnızca yeni video üretildiği, eski içeriğin kopyalanmadığı, resmi indirme sonrası dosya doğrulandığı ve Gemini'de açılabilir link bulunduğu zaman `E2E_GENERATION_PASS` de. Gerçek Instagram yayını deneme sırasında yapılmaz. Antigravity sürümünde Automations yoksa alternatif zamanlayıcıya geçmeden önce gerçek resmî dokümana göre kurulumu doğrula.

## HER GÜNÜN KISA RAPORU
Tarih, hizmet, seçilen özgün fikrin kısa özeti, gerçekten tıklanan Create Video aracı, üretilen yeni media ID/URL, MP4 SHA-256, dosyanın teknik bilgileri, kullanılan üretim kotası (biliniyorsa), `AWAITING_APPROVAL` veya kesin hata kodu. Bir gün başarısızsa ertesi gün kendiliğinden geçmiş MP4'ü sunma.


## GÖRSEL QC GÜVENLİK KAPISI (2026-11-08 HATA DÜZELTMESİ)
ÖNEMLİ: Önceki 20 saniyelik video ilk 10 saniye alakasız telefonla web sitesi anlatımı, sonraki 10 saniye sınav otomasyonu oldu. Bu video visual QA'de FAIL; codec ve çözünürlük PASS olması yeterli değildir. Telefonu kameraya uzatıp kendi ekranına bakıyormuş gibi davranmak gibi fiziksel tutarsızlıklar reddedilir.

Her yeni MP4 için `python -m src.visual_review --video "<dosya.mp4>"` komutuyla zaman etiketli inceleme kareleri çıkar. Dosyadaki kareleri 0, 2, 4, ... saniye boyunca tek tek GÖRSEL olarak incele; önemli hikâye dönüm noktalarında ara kareleri ve sesli videoyu da kontrol et. Kod yalnızca kare çıkarmaya yarar, anlam denetimini sen yaparsın. Kurgunun 0-10 saniyesi WEB, 10-20 saniyesi SINAV ise `VISUAL_QC_FAILED` ve zaman damgalarını raporla. Yanlış kamera açısı, aktörün bakışıyla çelişen telefon yönü, gerçek olmayan UI, bozuk logo, aşırı vaat ve kontrolsüz sahne değişikliği de FAIL. `AWAITING_APPROVAL` durumuna ancak hem metadata hem visual QC geçtikten sonra gir. Hatalı videoyu paylaşma. Kullanıcı ek kullanım hakkı izni olmadan tekrar render harcama.
