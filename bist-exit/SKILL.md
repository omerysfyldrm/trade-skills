---
name: bist-exit
description: >-
  BIST Çıkış Planlayıcı (long). Girişten ÖNCE stop ve hedefi belirler, böylece
  ne zaman çıkacağını baştan bilirsin. Stop varsayılan açılış aralığının orta
  noktası (ya da aralık düşüğü, bir yüzde, ATR katı ya da verdiğin fiyat), kuruşa
  aşağı yuvarlanır; hedef 2R (ya da 1R, ya da verdiğin fiyat). Girişten yüksek
  stop'u, girişten düşük hedefi ve spread'e sığmayacak kadar dar stop'u reddeder,
  nedenini söyler. trader/plan.json yazar (timemachine, budget, alerts okur).
  Sadece long, emir YERLEŞTİRMEZ. "stop'um nerede", "stop ve hedef koy", "çıkışı
  planla", "ne zaman çıkayım", "R:R ne", "zarar durdur" dendiğinde ya da
  bist-entry tetikledikten hemen sonra, bist-timemachine'den önce kullan.
argument-hint: "[SEMBOL] [--stop-mode mid|low|pct|atr] [--rr 2]"
---

# bist-exit

Girişin riskini sen almadan önce tanımlar. `trader/entry.json`'dan girişi ve
açılış aralığını okur (ya da `--symbol X --entry F` ver).

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/exit.py"                        # entry.json'dan
python3 "${CLAUDE_SKILL_DIR}/exit.py" --stop-mode low        # stop aralık düşüğü
python3 "${CLAUDE_SKILL_DIR}/exit.py" --stop-mode pct --pct 2
python3 "${CLAUDE_SKILL_DIR}/exit.py" --stop-mode atr --atr-mult 1.5
python3 "${CLAUDE_SKILL_DIR}/exit.py" --symbol THYAO --entry 309 --stop 305 --rr 2
```

- Stop varsayılanı aralık orta noktası; hedef giriş + `rr`×R.
- `trader/plan.json` yazar: `entry, stop, target, risk_per_share, rr, flat_by`.
- Gün içi: `flat_by` 17:55 — pozisyonu gün sonu kapat.
