---
name: piyasa-duygu
description: >-
  Piyasa Duygu / Makro & Lider Haber Analizi (haber tabanlı). Kullanıcı "piyasa
  havası", "makro ne durumda", "risk açık mı", "lider haberleri", "Fed ne dedi",
  "gündem ne", "piyasayı ne etkiliyor", "duygu analizi" dediğinde kullan.
  Piyasayı oynatan kişi ve kurumların (Fed/Powell, ECB, TCMB, Trump, enflasyon,
  jeopolitik, kripto regülasyon) haberlere yansıyan açıklamalarını çeker, basit
  sözlükle risk-açık/risk-kapalı tonu etiketler ve kısa makro brifing verir.
  BIST + ABD + kripto için ortak bağlam. Belirli X/Twitter hesapları KAZINMAZ
  (API gerekir); yalnızca haberlere yansıyan ifadeler okunur.
argument-hint: "[--topics 'ek sorgu'] [--per 4]"
---

# piyasa-duygu

Tek tek hisseye değil, genel rüzgâra bakar: liderlerin/merkez bankalarının
haberlere yansıyan açıklamaları ve makro başlıklar. Duygu sözlük tabanlıdır,
yön değil **bağlam** verir.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/duygu.py"                       # varsayılan 9 makro konu
python3 "${CLAUDE_SKILL_DIR}/duygu.py" --per 5
python3 "${CLAUDE_SKILL_DIR}/duygu.py" --topics "altın,doğalgaz,seçim"
python3 "${CLAUDE_SKILL_DIR}/duygu.py" --json
```

## Kapsam ve sınır
- Konular: Fed/Powell, ABD CPI, Trump/politika, ECB, TCMB, Türkiye ekonomi,
  jeopolitik/petrol, kripto regülasyon, BIST/yabancı akışı.
- Kaynak: Google News RSS (tr + en). **Sosyal medya hesap analizi değildir** —
  X/Twitter API'siz okunamaz; bu skill liderlerin söylediklerinin habere
  yansımasını okur.
- Ton sözlük tabanlı; kesin yön değil, risk-açık/kapalı bağlamı verir. Alım-satım
  kararını tek başına buna dayandırma.
