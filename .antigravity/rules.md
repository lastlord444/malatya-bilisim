# Project rules — Malatya Bilişim Reels Factory

- Bu çalışma alanı: `malatya-bilisim`. Yeni proje klasörü oluşturma. Önce `git status`; mevcut yerel değişiklikleri ezme.
- DÖRT hizmet: eğitim kurumları sınav/bursluluk otomasyonu, kuruma özel web yazılımı, iş süreçleri için AI ajanları, markaya özel AI sosyal medya yönetimi. Her Reels tek hizmet, tek hedef kişi, tek doğrulanabilir fayda.
- Her günün fikrini ve promptunu ajanın kendisi YENİDEN tasarlaması zorunlu. `config/content_strategy.json` + `python -m src.daily_brief` + `prompts/creative-director.txt` + `prompts/video-generation.txt` oku. Tek şablon video tekrarına düşme.
- Günlük görev = **Antigravity Automations**, her defasında temiz ajan oturumu. `/schedule` komutunu kalıcı oturumlar arası servis sanma. Asıl talimat `automations/daily_reels_agent.md`.
- Gerçek Gemini üretimi: yeni Gemini konuşması → + / Video oluştur aracı → 9:16 → yeni sahneye özel prompt → gönder → üretim tamamlandı kanıtı → resmî MP4 indirmesi → metadata/SHA-256 → kullanıcıya Gemini video bağlantısı.
- Daha önce var olan videonun indirilmesi **üretim değildir**. Promptun üretilmesi **video değildir**. API isteğinin kabul edilmesi **Instagram'da yayımlandı** değildir.
- Ses/insan/Türkçe diyalog olabilir, ancak doğal dudak senkronu, anlaşılır altyazı, izinli materyal ve doğru Türkçe kontrol edilmeli. 8 saniye evrensel şart değil; gerçek araç ve kota belirleyici.
- Kullanıcı açık onayı olmadan Instagram yayını yok. Para harcayan API çağrısı, abonelik satın alımı, yeni ücretli üretim veya mevcut kotanın dışına çıkmak yok.
- `.env`, çerezler, kişisel videolar, ekran görüntüleri ve özel içerik geçmişi public Git'e gönderilmez. GitHub depo sürümü ile VDS çalışma ağacını karşılaştır, zorla reset/push yapma.
- Üretim/indirme/kalite/yayın için gerçek PASS, FAIL, BLOCKED ve NOT_TESTED durumları kullan; başarılmadıysa açıkça bildir.
