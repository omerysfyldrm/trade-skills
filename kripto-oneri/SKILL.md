---
name: kripto-oneri
description: >-
  Kripto Çok-Zaman-Dilimli Öneri (7/24). Kullanıcı "kripto tara", "kripto öner",
  "hangi coini alayım", "BTC/ETH nasıl", "uzun vade kripto", "altcoin öner"
  dediğinde kullan. Gün içi + haftalık + aylık + yıllık tutuş için likit
  coinlerden adaylar; HER öneri teknik (hareketli ortalamalar SMA20/50/200,
  RSI, momentum, 52h, golden/death cross) + haber (ETF, listeleme, hack,
  regülasyon, ortaklık, halving) gerekçesiyle. Veri Yahoo (BTC-USD, ETH-USD...),
  7/24. Alım-satımı KULLANICI yapar; emir yok. Kripto çok oynaktır, kaldıraç/
  vadeli ÖNERİLMEZ.
argument-hint: "[--bucket gun_ici|haftalik|aylik|yillik|all] [--top 5]"
---

# kripto-oneri

BIST ve ABD öneri motorunun aynısı, kripto evreninde. Kripto 7/24 işlem görür;
borsa saati yoktur ama oynaklık çok yüksektir.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/kripto.py"                       # 30 likit coin, 4 kova, haberli
python3 "${CLAUDE_SKILL_DIR}/kripto.py" --bucket aylik --top 8
python3 "${CLAUDE_SKILL_DIR}/kripto.py" --symbols BTC-USD,ETH-USD,SOL-USD
python3 "${CLAUDE_SKILL_DIR}/kripto.py" --no-news --json      # hızlı, teknik
```

- Evren: BTC, ETH, BNB, SOL, XRP, ADA, AVAX, DOGE, LINK ve diğer likitler (-USD).
- Teknik: `_bistlib/indicators`; haber: Google News + kripto katalizör filtresi.
- **Uyarı:** Kripto spot bile çok oynaktır; 2000 TL gibi küçük hesapta pozisyonu
  küçük tut, kaldıraç/vadeli alma. Alım-satım sana ait.
