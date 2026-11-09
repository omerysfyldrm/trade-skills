# BIST Trader skill paketi (13 skill)

ABD odaklı day-trader-skill'in BIST'e uyarlanmış kardeşi. Veri katmanı
`_bistlib/`: Yahoo `.IS` chart (fiyat, TRY), Google News RSS (haber + KAP
bildirimleri), Borsa İstanbul takvimi (10:00–18:00). KAP ham API'si ve İş
Yatırım botlara kapalı olduğu için tarayıcı taklidi YAPILMAZ; meşru beslemeler
kullanılır, gated veriler (takas, derinlik, bilanço tablosu) yapıştırmayla gelir.

## Akış (tek işlem)
bist-endeks (rejim) → bist-scanner → bist-news → bist-entry → bist-exit →
bist-timemachine → bist-budget → bist-risk → bist-broker (elle Midas)
bist-alerts: açıkken stop/hedef/17:55 | bist-analyst, bist-takas, bist-derinlik: ek analiz

## Skiller
scanner, news, entry, exit, timemachine, budget, risk, broker(elle Midas),
alerts, analyst, endeks, takas(yapıştır), derinlik(yapıştır)

## Ayar
`trader/config.json` (örnek: bist-budget/config.example.json): hesap TL,
işlem başı azami zarar, günlük limit, R:R, giriş penceresi, kesirli lot.

## Sınırlar
- Midas emir bağlayıcısı yok → emirler elle girilir (bist-broker fiş üretir).
- Takas/derinlik/ham bilanço: ücretsiz API yok → Midas/İş Yatırım'dan kopyala-yapıştır.
- Yatırım tavsiyesi değildir. Çoğu gün içi işlemci para kaybeder.
