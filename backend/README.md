# OltaRotası API

FastAPI başlangıç servisi; gerçek habitat/çevresel veri ve öneri modeli henüz bağlı değildir.

- GET /health: process liveness.
- GET /ready: PostgreSQL/PostGIS bağlantısı; veri kapsamı hazır olduğu anlamına gelmez.
- GET /v1/species, /v1/regions: katalog.
- POST /v1/search: species_id, region, timezone içeren starts_at/ends_at. Şimdilik açık data_unavailable sonucu ve null koşullar.

Test: `python -m pytest tests` (backend dizininde).

VPS: `/home/furkanozturk/MyProjects/olta_rotasi`.
Docker Compose API'yi yalnız 127.0.0.1:7030'a açar. DB dışa port açmaz. Nginx TLS sonlandırır.
Şifre deploy/.env içinde sunucuda üretilir; depoya alınmaz. İlk DB oluşturulduktan sonra yalnız .env değişikliği DB parolasını değiştirmez.
Kurulum: `sudo bash deploy/install.sh`. Script mevcut aktif Games config üzerine yazmaz. Sertifika geçerliliğini kontrol eder. Sertifika yenilemesi ayrıca Certbot renewal yapılandırmasıyla doğrulanmalıdır.
Geri alma: ilgili Nginx linkini kaldırıp eski retired yapılandırmasını geri yükle; `nginx -t` ve reload. Servisleri durdurmak için `sudo docker compose -f deploy/compose.yaml down`; veri volume'u korunur. `down -v` veri siler, rutin işlem değildir.
VPS Ubuntu 25.04 destek dışı; desteklenen sürüme geçiş planı sürüyor. Harici eski proje DB'leri henüz temizlenmedi.

POST /v1/point: latitude/longitude (İzmir pilot kutusu) → gerçek EMODnet DTM 2024 en yakın grid hücresi. Yanıtta depth_m, grid koordinatı, interpolation, LAT referansı ve kaynak/erişim tarihi. no_data ve non_negative_elevation derinlik sıfır değildir. Kaynak erişim sorunu 503. Habitat/yakalama yüzdesi henüz unavailable/null. Bu değer navigasyon veya kıyıda hassas ölçüm için değildir.

POST /v1/forecast: aynı İzmir point payload → bugün dahil 7 Türkiye günü; yalnız gelecek saatler, hava sıcaklığı, yağış olasılığı/miktarı, bulut, rüzgâr/hızı/yönü/hamlesi, MSL basınç ve 3 saat farkı. Kaynak Open-Meteo; yakın weather grid kullanılır. 15 dakikalık, 128 sorguluk process cache; hava başarısızlığı derinliği etkilemez. forecast_retrieved_at veri alma tarihidir; sağlayıcının model run tarihi bilinmiyor/null. Gün özetleri tüm yerel günün tahminidir; ilk gün geçmiş saatleri de içerebilir, saatlik detay yalnız gelecek saatleri gösterir.

İlk başarılı sorguda forecast_snapshots PostgreSQL tablosu CREATE IF NOT EXISTS ile hazırlanır; ham sağlayıcı yanıtı, koordinat ve erişim tarihi saklanır. DB archive sorunu tahmini engellemez, archive_status=unavailable olur; stored durumu canlıda kontrol edilmeli. Mevcut database volume kullanılır; yeniden başlatma arşivi silmez. Arşivden erişim API'si henüz yok. Pilot dışına yayın öncesi retention, indeks, quota/rate-limit ve migration düzeni tamamlanmalı.

Open-Meteo Free API yalnız ticari olmayan kişisel pilot içindir; https://open-meteo.com/en/terms ve https://open-meteo.com/en/docs kontrol edildi. Veri CC BY 4.0 attribution ile. Ticari yayın için ücretli hizmet/uygun sağlayıcı gerekir. OPEN_METEO_API_KEY varsa adaptör customer-api host kullanır; Compose'a env aktarımı ayrıca yapılandırılmalı, mevcut compose anahtar içermez. Key/URL loglanmaz veya arşivlenmez. Deniz sıcaklığı/dalga/akıntı ve ay bu endpoint'te henüz yok.
