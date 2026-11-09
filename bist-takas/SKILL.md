---
name: bist-takas
description: >-
  BIST Aracı Kurum Dağılımı & Takas Analizi. Hangi aracı kurumun net alıp
  sattığı ve takas yoğunlaşması verisi İş Yatırım/Matriks gibi bot-korumalı/
  ücretli kaynaklardadır; otomatik çekilemez. Sen Midas/İş Yatırım'da bu
  tabloya erişiyorsun: kopyalayıp bir .txt'ye yapıştır, bu skill yapılandırır
  ve sinyale çevirir — net alıcılar/satıcılar, net para akışı, ilk-3 kurum
  yoğunlaşması ve toplama/dağıtım işareti. "aracı kurum dağılımı", "takas
  analizi", "kim topluyor", "hangi kurum alıyor", "takas verisi" dendiğinde
  kullan. Veri YAPIŞTIRMA ile gelir; canlı çekmez.
argument-hint: "--paste takas.txt [--symbol THYAO] [--top 5]"
---

# bist-takas

Aracı kurum dağılımı ve takas tek başına yön vermez ama kimin topladığını/
dağıttığını gösterir. Veri bot-korumalı kaynaklarda olduğu için otomatik
çekilmez; sen Midas/İş Yatırım'dan kopyalar, skill analiz eder.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/takas.py" --paste takas.txt --symbol THYAO
python3 "${CLAUDE_SKILL_DIR}/takas.py" --paste takas.txt --top 8 --json
```

## Yapıştırma biçimi
Her satırda bir kurum adı + sayılar (Türk biçimi: nokta binlik, virgül ondalık):
```
AK YATIRIM          2.000.000   500.000   1.500.000     # Ad  Alış  Satış  Net
GARANTİ YATIRIM     1.250.000   800.000   450.000
İŞ YATIRIM          900.000     1.100.000  -200.000
```
"Ad Net" (tek sayı) ya da "Ad Alış Satış" (net hesaplanır) de kabul edilir.
Sütunlar boşlukla ayrılmalı; binlik ayracı NOKTA olmalı.

## Çıktı
Net alıcılar/satıcılar listesi, toplam net akış, ilk-3 alıcı yoğunlaşması ve
toplama/dağıtım sinyali. **Fiyat, hacim ve haberle birlikte** oku; takas gecikmeli
ve tek başına yanıltıcı olabilir. Ham tabloyu Claude'a da gösterebilirsin,
rakamları birlikte yorumlarız.
