# Av olasılığı: tasarım, henüz uygulanmadı

13 Ekim 2026. Bilimsel kaynak incelemesi frontend reposundaki `docs/CATCH_PROBABILITY_RESEARCH.md` içindedir.

Hedef: yer/tür/yöntem/zaman/süre koşullu en az bir hedef balık yakalama olasılığı. Başlangıç önerisi bir kişi ve iki saatlik kıyı avıdır; mevcut arama zaman aralıkları değiştirilmedi.

## Gerekli veri

- Başarılı ve sıfır sonuçlu av oturumları; hedef tür, konum, aktif süre, yöntem, yem/sahtesi, olta sayısı, kullanıcı/oturum gruplama kimliği ve kayıt doğrulama durumu.
- Habitat, erişilebilir derinlik, mevsim, güneş saati, su sıcaklığı, rüzgâr/kıyı yönü, dalga, akıntı, basınç/değişimi ve ay aday değişkenleri.
- Kaynak/birim/çözünürlük ve veri eksikliği; tahminin üretildiği ve geçerli olduğu zaman. Gelecek önerilerinin testi için tahmin arşivi.

## Yayın kapıları

Yer ve tür kapsamı doğrulanmalı; yeterli başarılı/başarısız efor kaydı bulunmalı. Ayrı zaman/yer testleri ve eğitimden ayrı kalibrasyon gerekir. Güvenilirlik grafikleri, Brier/log-loss, belirsizlik ve basit referans kıyaslanır. Basınç/ay katkısı çıkarma deneyleriyle ölçülür. Gösterilecek yüzde, koşul puanının yeniden adlandırılması olamaz.

Kalibre edilmemiş veya kapsam dışı durumda mevcut `catch_probability: null` korunur. Veri yokluğu, erişim/yasal engel ve düşük av ihtimali farklı durumlardır. API şu anda değişmedi.

## İleride tasarlanacak sözleşme

Olasılık yanında olay tanımı, av süresi/yöntemi, model sürümü, kalibrasyon durumu/kapsamı, tahmin üretim zamanı ve veri güncelliği bulunmalı. Tahmin belirsizliği, habitat sınıflama güveni ve yakalama olasılığı ayrı alanlardır. Saatlik yüzdeler toplanarak günlük yüzde üretilmez.

## Sonraki sıra

1. İzmir küçük pilotunda habitat/batimetri kapsam kontrolü.
2. Saatlik çevresel veri adaptörleri ve tahmin arşivi.
3. Önceden başlatılan ve sıfır sonucu da tutan av günlüğü.
4. Tür bazlı basit referans + açıklanabilir model; bağımsız test ve kalibrasyon.
5. Yalnız doğrulanmış kapsamda gün/saat yüzdesi.

Bu belgede kod, veri bağlantısı veya VPS değişikliği yapılmadı.
