#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ "$(id -u)" -ne 0 ]; then
  echo 'Çalıştırma: sudo bash deploy/install.sh' >&2
  exit 1
fi
openssl x509 -in /etc/letsencrypt/live/games.restinblocks.men/fullchain.pem -noout -checkend 0
openssl x509 -in /etc/letsencrypt/live/games.restinblocks.men/fullchain.pem -noout -checkhost games.restinblocks.men
chmod 755 ../backend/db
chmod 644 ../backend/db/*.sql
# Do not print the resolved Compose config: it contains a database password.
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 180
curl --fail --silent http://127.0.0.1:7030/ready
source_file="$PWD/games.restinblocks.men"
available=/etc/nginx/sites-available/games.restinblocks.men
enabled=/etc/nginx/sites-enabled/games.restinblocks.men
if [ -e "$enabled" ] || [ -L "$enabled" ]; then
  echo 'Games yapılandırması zaten aktif; üzerine yazılmadı.' >&2
  exit 1
fi
backup="$(mktemp /etc/nginx/sites-available/olta-backup.XXXXXX)"
if [ -e "$available" ]; then
  cp -L "$available" "$backup"
else
  rm "$backup"
fi
install -o root -g root -m 644 "$source_file" "$available"
ln -s "$available" "$enabled"
if nginx -t && systemctl reload nginx; then
  echo 'OltaRotası backend kurulumu tamamlandı.'
else
  rm -f "$enabled"
  if [ -f "$backup" ]; then cp "$backup" "$available"; else rm -f "$available"; fi
  echo 'Nginx değişikliği geri alındı; containerlar yerel portta çalışıyor.' >&2
  exit 1
fi
