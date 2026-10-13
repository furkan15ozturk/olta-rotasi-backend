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
