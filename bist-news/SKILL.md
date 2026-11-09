---
name: bist-news
description: >-
  BIST Haber Takipçisi. İzlenen her hisse için Türkçe haber başlıklarını
  çeker (Google News RSS); bu besleme KAP bildirimlerini de ("KAP *** XXX
  ***") başlık olarak getirir. Sadece son kontrolden bu yana YENİ olanı
  gösterir, en yenisi üstte, günün yüzde değişimiyle; her haberi etiketler
  (KAP, bilanço, temettü, analist, sermaye, ihale...) ve tekrarı atar.
  "BIST haber", "THYAO'da ne var", "neden yükseldi/düştü", "KAP bildirimi
  var mı", "sabah bülteni", "izleme listemde haber", "bir şey çıktı mı"
  dendiğinde ya da bist-scanner kurulum bulduktan sonra kullan.
argument-hint: "[--symbols A,B] [--kap-only] [--all]"
---

# bist-news

İzlediğin hisselerde kırılan haberi ve KAP bildirimlerini tek yerde toplar.
Kaynak Google News RSS (Türkçe, TR); KAP'ın kendi API'si botlara kapalı
olduğu için tarayıcı taklidi YAPILMAZ — bunun yerine KAP bildirimleri zaten
bu meşru beslemede başlık olarak gelir.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/news.py"                       # watchlist.json'daki hisseler, sadece yeni
python3 "${CLAUDE_SKILL_DIR}/news.py" --symbols THYAO,GARAN # elle liste
python3 "${CLAUDE_SKILL_DIR}/news.py" --all                 # yeni filtresi olmadan hepsi
python3 "${CLAUDE_SKILL_DIR}/news.py" --kap-only            # sadece KAP bildirimleri
python3 "${CLAUDE_SKILL_DIR}/news.py" --json
```

- `trader/watchlist.json`'daki `hits[].symbol`'ü okur (yoksa `--symbols` ver).
- Görülen başlıkları `trader/news_seen.json`'a yazar; bir dahaki sefere tekrar
  göstermez.
- Başlıklar teyit için; işlem kararını tek bir habere dayandırma.
