---
name: bist-scanner
description: >-
  BIST Grafik Tarayıcı. Binlerce yerine likit BIST-100 grafiğini tarar:
  20 günlük kapanış-zirvesi kırılımı, boğa bayrağı, 20 günlük ortalamayı
  geri alma, aşırı satım ve aşırı satım tepkisi; ayrıca gün içi açılış
  aralığı kırılımı (İstanbul 10:00 açılışına göre, 5 dakikalık barlar).
  Ücretsiz Yahoo .IS verisi (TRY), bar bar. trader/watchlist.json yazar;
  bist-news ve bist-entry bunu okur. "piyasayı tara", "BIST tara", "kırılım
  var mı", "açılış aralığı", "boğa bayrağı", "aşırı satım", "bugün neye
  bakayım", "izleme listesi kur" dendiğinde ya da işlem gününün başında
  bist-news'ten önce kullan.
argument-hint: "[universe | daily | orb] [--symbols A,B] [--show N]"
---

# bist-scanner

Günlük işlemin ilk adımı. Yahoo'nun ücretsiz `.IS` grafiklerini okur ve bir
kurala uyan hisseleri listeler. Bir tarama = kurala uyan grafikler listesi,
alınacak hisse listesi DEĞİL; grafikteki kurulum bir tahmin değil. Çoğu gün
içi işlemci para kaybeder; tarayıcı bunu değiştirmez, sadece elle 100 grafik
çevirmekten kurtarır.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/scan.py" universe                      # -> trader/universe.txt (Yahoo'ya karşı doğrular)
python3 "${CLAUDE_SKILL_DIR}/scan.py" daily                         # açılış öncesi günlük kurulumlar -> trader/watchlist.json
python3 "${CLAUDE_SKILL_DIR}/scan.py" daily --symbols THYAO,GARAN   # ya da --watchlist FILE, --limit 100
python3 "${CLAUDE_SKILL_DIR}/scan.py" orb                           # bugünün açılış aralığı kırılımı
python3 "${CLAUDE_SKILL_DIR}/scan.py" orb --or-minutes 15 --show 20
python3 "${CLAUDE_SKILL_DIR}/scan.py" orb --now "2026-11-10 10:30"  # saati sabitle (İstanbul)
```

Seçenekler: `--min-price`, `--min-volume`, `--limit N`, `--show N`,
`--no-write`, `--json`, `--pause SANIYE`. Çıkış kodu: bulduysa 0, bulmadıysa 1.

## Ne okur, ne yazar
| dosya | ne |
| --- | --- |
| `bist100.txt` | gömülü evren (bu klasörde); `universe` bunu Yahoo'ya karşı doğrular |
| `trader/universe.txt` | `universe`'ün yazdığı canlı semboller; `daily`/`orb` okur |
| `trader/watchlist.json` | `daily`/`orb`'un yazdığı `hits[]`; bist-news ve bist-entry okur |

## Kurulumlar (günlük)
- **20g-zirve-kirilim**: son 20 günün kapanış zirvesini aştı.
- **20g-ort-geri-aldi**: 20 günlük ortalamanın altından üstüne geçti.
- **boga-bayragi**: sert yükseliş + dar sıkışma, ortalamanın üstünde.
- **asiri-satim / asiri-satim-tepki**: 7 günde sert düşüş / düşüşten yeşil dönüş.

## Önemli
- **Borsa İstanbul saatleri** gömülüdür (hafta içi 10:00–18:00, 2026-2027
  tatilleri). Hafta sonu/tatilde `orb` canlı olmaz; uyarı verir.
- Para birimi **TRY**. Sıradaki akış: bist-news → bist-entry → bist-exit →
  bist-timemachine → bist-budget → bist-risk → bist-broker.
