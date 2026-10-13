# Güncel durum — 2026-10-13

VPS: furkanozturk@57.131.22.192, /home/furkanozturk/MyProjects/olta_rotasi.
API loopback 7030; planlanan HTTPS games.restinblocks.men.
Dört API testi geçti. İlk Docker kurulumunda initdb dizin izinleri nedeniyle DB başlamadı. Remote db klasörü 755 ve SQL dosyası 644 yapıldı. Kurulum tekrar çalıştırıldı ve 2026-10-13 tarihinde yayın doğrulandı.
VPS sudo şifre istiyor ve kullanıcı Docker grubunda değil. Parola/anahtar repoda yok.
Eski Pomodoro/Memoria/Games dosyaları yedeklenip kaldırıldı. Harici eski DB'ler incelenmedi. Ubuntu 25.04 destek dışı, yükseltme planı gerekli.
Veri katmanları, hava API, av modeli ve Flutter bağlantısı sıradaki işler.
Frontend ayrı repo; burası backend + deploy klasör yapısını korur.

## API container izin düzeltmesi
PostgreSQL kullanıcı çıktısında healthy. API kodu aktarımdan sonra 700/600 root sahipliğiyle imaja alındığından non-root appuser okuyamıyordu. Dockerfile COPY --chown=10001:10001 ile düzeltildi; macOS ._* dosyaları build context dışına alındı. Yeniden build sonrası API ve DB healthy. VPS loopback /ready ve HTTPS /health + /ready doğrulandı; dış istemciden HTTPS /health service=olta-rotasi yanıtı alındı.

## Canlı kurulum doğrulaması — 2026-10-13
Nginx test/reload başarılı. https://games.restinblocks.men altında OltaRotası 0.1.0 çalışıyor. TLS doğrulaması bypass edilmedi. /ready PostGIS bağlantısını doğruluyor, habitat_data=unavailable; gerçek mera/hava modeli henüz bağlı değil. Sonraki iş Flutter API entegrasyonu ve veri katmanları.

## Av olasılığı araştırması — 2026-10-13
Kullanıcı veri entegrasyonundan önce bilimsel araştırma ve ileride gün/saat bazlı yüzde istedi. Frontend `docs/CATCH_PROBABILITY_RESEARCH.md` kaynakları, kanıt sınırlarını, tür ayrımlarını, av eforu/sıfır av kayıtlarını, model/kalibrasyon ve sade UI önerisini içerir. Backend `docs/PROBABILITY_MODEL.md` uygulama kapılarını kaydeder. İki saatlik en az bir hedef balık olayı önerildi; henüz ürün/API kararı uygulanmadı. Basınç ve ay aday girdiler; etkileri sabit katsayıyla varsayılmaz. Model kalibre edilene kadar yüzde null kalır. Bu aşama yalnız dokümantasyon; gerçek veri veya sunucu değişikliği yok.

## T02 gerçek nokta derinliği — 2026-10-13
POST /v1/point eklendi. İzmir kutusunda adlandırılmış latitude/longitude doğrulaması; EMODnet DTM 2024 elevation/interpolation_flag tek hücre sorgusu, grid koordinatı/LAT referansı/güncellik/provenance, no-data ve negatif olmayan kot ayrımı, timeout/503. Yedi API/veri testi geçti. Gerçek adaptör 38.35/26.65 sorgusunda ~3.2 m, interpolated=true döndürdü; bu hassas kıyı ölçümü değildir. main.py/bathymetry.py VPS mevcut proje dizinine SCP ile aktarıldı. sudo -n kontrolü parola gerektirdi: çalışan container henüz yeniden derlenmedi; /v1/point canlıda henüz yok. Kullanıcı VPS'de `cd /home/furkanozturk/MyProjects/olta_rotasi && sudo docker compose -f deploy/compose.yaml up -d --build --wait api` çalıştırmalı. Ardından HTTPS /v1/point doğrulanacak. Arayüz refinement sonraya bırakıldı; sıradaki T03 7 günlük hava.
