# OltaRotası backend

Başlangıçta HANDOFF.md ve backend/README.md oku. Kullanıcıyla Türkçe konuş.
Frontend ayrı repo: furkan15ozturk/olta-rotasi-frontend.
Derinlik ve hava canlı bağlıdır; katmanların güncel yayın/doğrulama durumunu HANDOFF.md üzerinden kontrol et. Habitat ve av modeli henüz yok. Eksik verileri unavailable/null olarak döndür; yakalama yüzdesi uydurma.
İzmir pilotu, kıyı olta öncelikli. Hava, rüzgâr, özellikle basınç değişimi ve ay olayları öneri modelinde araştırılacak.
Şifre/SSH anahtarı/.env dosyasını commit etme. Docker config çıktısı parola içerir, paylaşma.
API değişiminde backend/tests testlerini çalıştır. Deploy scriptlerinde bash -n ve imkan varsa compose config --quiet kontrolü yap.
VPS'de diğer projeleri koru. Kullanıcı sudo şifresini paylaşmaz; gereken root adımları için hazır script ver.
Son durumda HANDOFF.md güncelle. Tamamlanan işleri ilgili GitHub reposuna commit/push yap; sonucu doğrula.
