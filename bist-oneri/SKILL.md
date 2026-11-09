---
name: bist-oneri
description: >-
  BIST Çok-Zaman-Dilimli Hisse Önerisi — ANA tarama. Kullanıcı "bist'i tara",
  "hisse öner", "ne alayım", "haftalık/aylık/yıllık tutabileceğim hisse",
  "uzun vade ne", "yatırımlık hisse" dediğinde bunu kullan. Gün içi + haftalık +
  aylık + yıllık tutuş için ayrı ayrı adaylar üretir; HER öneriyi hem teknik
  (grafik, hareketli ortalamalar SMA20/50/200, EMA, RSI, momentum, 52h zirve,
  golden/death cross) hem temel (haber, KAP bildirimi, anlaşma/ihale/yatırım/
  bilanço/temettü başlıkları) gerekçesiyle verir. Tek günlük veri çekip
  haftalık/aylık grafiği türetir. Alım-satımı KULLANICI yapar; hiçbir emir
  yerleştirilmez. Gün içi 5dk giriş anı için ayrıca bist-scanner/bist-entry.
argument-hint: "[--bucket gun_ici|haftalik|aylik|yillik|all] [--top 5]"
---

# bist-oneri

"bist'i tara" dendiğinde dört zaman dilimi için gerekçeli aday listesi çıkarır.
Bir tarama/sıralamadır, kehanet ya da alım emri değildir; çoğu işlemci para
kaybeder. Gerekçeler şeffaftır — oku, körlemesine alma.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/oneri.py"                        # 4 kova, BIST-100, haberli
python3 "${CLAUDE_SKILL_DIR}/oneri.py" --bucket aylik --top 8
python3 "${CLAUDE_SKILL_DIR}/oneri.py" --symbols THYAO,GARAN,ASELS
python3 "${CLAUDE_SKILL_DIR}/oneri.py" --no-news --json       # hızlı, sadece teknik
```

## Kovalar ve mantık
- **Gün içi**: 20g zirveye yakınlık + hacim artışı + 20g ortalama üstü (momentum).
  Canlı 5dk giriş için bist-scanner `orb` + bist-entry'e devret.
- **Haftalık** (günler–haftalar): yukarı trend, RSI sağlıklı, 50g üstü, zirveye yakın.
- **Aylık** (haftalar–aylar): 200g üstü (ana trend), haftalık grafik ortalama üstü,
  golden cross, dipten uzak.
- **Yıllık** (uzun vade): aylık grafik boğa, 200g'nin belirgin üstünde, ölüm
  kesişimi yok, uzun vadeli yükselen seri.

## Gerekçeler
- **Teknik**: `_bistlib/indicators.py` (ortalamalar, RSI, momentum, cross, 52h).
- **Temel**: Google News + KAP başlıkları (anlaşma, ihale, yatırım, bilanço,
  temettü...). Ham bilanço rakamı için `bist-analyst SEMBOL --paste tablo.txt`.

## Sınır
BIST ham bilançosu (KAP XBRL/İş Yatırım) botlara kapalıdır; temel analiz haber +
yapıştırma ile derinleşir, otomatik finansal tablo çekilmez. Alım-satım kullanıcıya aittir.
