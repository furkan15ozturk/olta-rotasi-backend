# Güncel durum — 2026-10-13

VPS: furkanozturk@57.131.22.192, /home/furkanozturk/MyProjects/olta_rotasi.
API loopback 7030; planlanan HTTPS games.restinblocks.men.
Dört API testi geçti. İlk Docker kurulumunda initdb dizin izinleri nedeniyle DB başlamadı. Remote db klasörü 755 ve SQL dosyası 644 yapıldı. Kullanıcı sudo deploy/install.sh ile kurulumu tekrar çalıştırmalı; yayın henüz doğrulanmadı.
VPS sudo şifre istiyor ve kullanıcı Docker grubunda değil. Parola/anahtar repoda yok.
Eski Pomodoro/Memoria/Games dosyaları yedeklenip kaldırıldı. Harici eski DB'ler incelenmedi. Ubuntu 25.04 destek dışı, yükseltme planı gerekli.
Veri katmanları, hava API, av modeli ve Flutter bağlantısı sıradaki işler.
Frontend ayrı repo; burası backend + deploy klasör yapısını korur.

## API container izin düzeltmesi
PostgreSQL kullanıcı çıktısında healthy. API kodu aktarımdan sonra 700/600 root sahipliğiyle imaja alındığından non-root appuser okuyamıyordu. Dockerfile COPY --chown=10001:10001 ile düzeltildi; macOS ._* dosyaları build context dışına alındı. Yeniden build ve canlı sağlık doğrulaması bekleniyor. Yerel 7030 erişilemiyor; mevcut HTTPS {status:ok} OltaRotası yayını kanıtı değildir.
