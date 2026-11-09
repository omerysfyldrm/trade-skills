---
name: us-oneri
description: >-
  ABD Borsası Çok-Zaman-Dilimli Hisse Önerisi. Kullanıcı "ABD'yi tara", "US
  hisse öner", "Amerikan borsası", "NVDA/AAPL nasıl", "uzun vade ABD hissesi",
  "hangi Amerikan hissesi" dediğinde kullan. Gün içi + haftalık + aylık + yıllık
  tutuş için likit ABD hisselerinden adaylar; HER öneri teknik (hareketli
  ortalamalar SMA20/50/200, EMA, RSI, momentum, 52h, golden/death cross) +
  haber (İngilizce: earnings, guidance, upgrade, deal, buyback...) gerekçesiyle.
  Ham bilanço/temel için trader-analyst SEC EDGAR'dan okur. Alım-satımı KULLANICI
  yapar; emir yerleştirilmez.
argument-hint: "[--bucket gun_ici|haftalik|aylik|yillik|all] [--top 5]"
---

# us-oneri

BIST/kripto öneri motorunun aynısı, ABD evreninde; haberler İngilizce çekilir.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/us.py"                           # 50 likit ABD hissesi, 4 kova
python3 "${CLAUDE_SKILL_DIR}/us.py" --bucket yillik --top 8
python3 "${CLAUDE_SKILL_DIR}/us.py" --symbols AAPL,NVDA,MSFT
python3 "${CLAUDE_SKILL_DIR}/us.py" --no-news --json
```

- Evren: AAPL, NVDA, MSFT, AMZN, META, TSLA ve diğer mega/large-cap + popüler
  işlem isimleri.
- Teknik: `_bistlib/indicators`; haber: Google News (en-US) + katalizör filtresi.
- **Derin temel analiz** (gerçek bilanço rakamları) için: `trader-analyst TICKER`
  — SEC EDGAR'dan gelir ve ABD'de otomatik çalışır (BIST'in aksine).
- ABD seansı İstanbul'la 16:30–23:00. Alım-satım sana ait.
