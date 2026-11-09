---
name: bist-analyst
description: >-
  BIST Bilanço/Analist Takibi. KAP'ın ham finansal XBRL'i botlara kapalı
  olduğundan meşru kaynaklardan okunabileni toplar: bir hisse için bilanço,
  temettü ve hedef-fiyat haberleri (Google News, KAP bildirimleri dahil),
  fiyatın 20 ve 50 günlük ortalamaya göre duruşu ve son çeyreklik getiri. Daha
  derin okuma için KAP bilanço tablosunu metin olarak --paste ile verirsen
  Claude özetler. "bilanço nasıl", "THYAO'yu analiz et", "bu çeyrek ne değişti",
  "temettü ne zaman", "hedef fiyat ne", "bilanço haftası mı", "bu hisse değer mi"
  dendiğinde ya da bir hisseyi bilanço dönemi çevresinde işlemeden önce kullan.
argument-hint: "SEMBOL [--paste dosya.txt]"
---

# bist-analyst

Bir hissenin finansal resmini, serbestçe erişilebilen veriyle özetler: fiyat
trendi (20/50g ortalama), son çeyrek getiri ve bilanço/analist/temettü haber
başlıkları. Gerçek bilanço tablosu için KAP metnini `--paste` ile ver; Claude
rakamları (gelir, marj, net kâr, EPS) o metinden özetler.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/analiz.py" THYAO
python3 "${CLAUDE_SKILL_DIR}/analiz.py" ASELS --paste bilanco.txt   # KAP metnini özetle
python3 "${CLAUDE_SKILL_DIR}/analiz.py" GARAN --json
```

- Yahoo `.IS` günlük kapanışları + Google News (finansal filtre).
- Ham bilanço rakamları için KAP/İş Yatırım tablosunu elle kopyalaman gerekir
  (bu kaynaklar otomatik erişime kapalı); `--paste` ile verdiğinde Claude okur.
