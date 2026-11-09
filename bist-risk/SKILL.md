---
name: bist-risk
description: >-
  BIST Risk Yöneticisi (TL). Her emri limitlerine karşı denetler ve aşanı
  broker'a gitmeden durdurur. Gün içi işlem için: stop zorunlu, stop'taki zarar
  işlem başı azami zarara sığmalı, R:R asgariyi geçmeli, günün toplam riski
  günlük zarar limitine sığmalı, günlük işlem sayısı aşılmamalı, giriş penceresi
  dışında ya da borsa kapalıyken yeni giriş yok, pozisyon üst sınırı. PASS ya da
  BLOCK, gerekçesiyle; kararı trader/risk_verdict.json'a yazar (bist-broker sadece
  PASS'ı gösterir). Çıkış asla günlük sınırla engellenmez. "emrimi kontrol et",
  "bu güvenli mi", "risk kontrolü", "kurallarımı bozuyor mu", "bu işlemi alabilir
  miyim", "bugün ne kadar riske girdim" dendiğinde ya da bist-broker'dan ÖNCE, her
  zaman kullan.
argument-hint: "[--now 'YYYY-MM-DD HH:MM']"
---

# bist-risk

Emir broker'a gitmeden son kapı. `trader/orders.json` ve `trader/plan.json`'ı
okur, `trader/config.json`'daki limitlere karşı denetler.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/check.py"
python3 "${CLAUDE_SKILL_DIR}/check.py" --now "2026-11-10 11:00"   # saati sabitle
python3 "${CLAUDE_SKILL_DIR}/check.py" --json
```

- Config limitleri: `max_loss_tl, daily_loss_limit_tl, max_trades_per_day,
  min_rr, entry_window, account_tl, position_cap_pct`.
- Günlük işlem ve risk sayımı `trader/journal.jsonl`'den gelir (bist-broker yazar).
- Borsa kapalıyken ya da giriş penceresi dışında yeni girişi BLOCK eder; çıkış
  serbesttir.
