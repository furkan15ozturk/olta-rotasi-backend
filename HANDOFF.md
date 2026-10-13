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
