---
name: bist-derinlik
description: >-
  BIST Emir Defteri (Kademe / Derinlik) Analizi. Gerçek zamanlı derinlik
  (Level 2) ücretsiz API'de yoktur; sadece Midas/Matriks'te canlı görünür. Sen
  oradaki kademe tablosunu kopyala, bir .txt'ye yapıştır; bu skill alış/satış
  hacim dengesizliğini, en büyük 'duvarları' (destek/direnç yığılmaları),
  spread'i ve alım-satım baskısını çıkarır. "derinlik analizi", "emir defteri",
  "kademe", "alış satış baskısı", "duvar var mı", "destek direnç kademe"
  dendiğinde kullan. Veri YAPIŞTIRMA ile gelir; canlı çekmez ve anlık değişir.
argument-hint: "--paste derinlik.txt [--symbol THYAO] [--split 308.5]"
---

# bist-derinlik

Emir defteri anlıktır ve ücretsiz çekilemez; Midas'ta canlı görürsün. Kademe
tablosunu kopyala-yapıştır, skill baskı ve duvarları çıkarsın.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/derinlik.py" --paste derinlik.txt --symbol THYAO
python3 "${CLAUDE_SKILL_DIR}/derinlik.py" --paste derinlik.txt --split 308.60   # fiyat-adet biçimi
```

## Yapıştırma biçimi
En sağlamı, kademe satırları (5-10 kademe), Türk sayı biçimiyle:
```
# Alış_Adet  Alış_Fiyat   Satış_Fiyat  Satış_Adet
1000         308,50       308,75       500
2000         308,25       309,00       1500
```
Alternatif: 'Fiyat Adet' çiftleri — bu durumda `--split <orta_fiyat>` ver
(örn son işlem fiyatı), altı alış/üstü satış sayılır.

## Çıktı
En iyi alış/satış, spread, alış-satış hacim dengesizliği (%), en büyük alış
duvarı (destek) ve satış duvarı (direnç), baskı sinyali. **Uyarı:** defter
hızla değişir ve sahte duvarlar (spoofing) olur; tek başına karar verme.
