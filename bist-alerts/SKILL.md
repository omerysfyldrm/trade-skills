---
name: bist-alerts
description: >-
  BIST Fiyat Alarmları. Plandan üç alarmı tek seferde kurar (stop, hedef ve
  'gün sonu düz' saati), ayrıca --above/--below ile elle seviye ve açılış zili.
  Borsa İstanbul saatlerini (10:00–18:00, 2026-2027 tatilleri) bilir, İstanbul
  saatini kendi hesaplar, Yahoo'dan gecikmeli fiyat çeker ve --check ile şu an
  hangi seviyenin çalmış olduğunu söyler. "şu seviyeye gelince haber ver",
  "THYAO 310'u görürse söyle", "stop'umu izle", "17:55'te kapat hatırlat",
  "borsa açık mı", "fiyat getir" dendiğinde ya da bist-exit plan yazdıktan sonra
  kullan.
argument-hint: "[SEMBOL] [--from-plan] [--above F] [--below F] [--check]"
---

# bist-alerts

Plandaki çıkış seviyelerini ve gün sonu kapanışı alarma çevirir, ya da elle
seviye koyar. Gerçek zamanlı push yoktur; `--check` ile o anki Yahoo fiyatına
göre çalanı bildirir (bir döngüde periyodik çağrılabilir).

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/alerts.py" --from-plan              # plan.json: stop+hedef+17:55
python3 "${CLAUDE_SKILL_DIR}/alerts.py" THYAO --above 310 --below 300
python3 "${CLAUDE_SKILL_DIR}/alerts.py" --from-plan --check      # şu an çalan var mı
```

- `trader/plan.json`'dan stop/hedef/`flat_by` okur; `trader/alerts.json` yazar.
- `--check` o anki fiyatı çeker ve çalan seviyeleri işaretler.
- Borsa durumunu (açık/kapalı/tatil) ve İstanbul saatini gösterir.
