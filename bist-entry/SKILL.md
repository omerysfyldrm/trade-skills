---
name: bist-entry
description: >-
  BIST Giriş Zamanlayıcı (long). Bir hisseyi 5 dakikalık barlarla izler,
  açılış aralığını (İstanbul 10:00'dan ilk 15 dk) kurar ve aralığın yüksekini
  ya da verilen bir seviyeyi (scanner'dan 20 günlük zirve gibi) KAPANIŞLA aşan
  ilk tamamlanmış barda girişi işaret eder; opsiyonel hacim şartıyla. Beklemede
  ve ne kadar kaldı, tetiklendi (saat + fiyat), süresi-doldu ya da açılmadı der;
  trader/entry.json yazar. Sadece long, emir YERLEŞTİRMEZ. "ne zaman gireyim",
  "THYAO'yu izle", "kırdı mı", "açılış aralığını geçti mi", "giriş sinyali"
  dendiğinde ya da bist-scanner ve bist-news'ten sonra, bist-exit'ten önce kullan.
argument-hint: "SEMBOL [--level F] [--now 'YYYY-MM-DD HH:MM']"
---

# bist-entry

Kurulumu bar bar izler ve long girişin ilk geçerli anını söyler. Girişi
yalnızca aralığı (ya da `--level`) KAPANIŞLA aşan tamamlanmış 5dk barında
verir — fitille değil.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/entry.py" THYAO                      # watchlist ilki de olur (argümansız)
python3 "${CLAUDE_SKILL_DIR}/entry.py" GARAN --level 145.6        # scanner seviyesini kır
python3 "${CLAUDE_SKILL_DIR}/entry.py" ASELS --min-vol-mult 1.5   # tetik barı hacim şartı
python3 "${CLAUDE_SKILL_DIR}/entry.py" THYAO --now "2026-11-10 10:30"  # saati sabitle
```

- Argümansız çağrıda `trader/watchlist.json`'ın ilk hissesini alır.
- `trader/entry.json` yazar (bist-exit okur): `status`, `entry`, `range_low/high`.
- Borsa açık değilse / aralık oluşmadıysa `açılmadı`, öğleden sonra `süresi-doldu` der.
