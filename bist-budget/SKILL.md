---
name: bist-budget
description: >-
  BIST Bütçe Yöneticisi (TL). Her pozisyonu bütçene ve işlem başına azami
  zararına göre boyutlandırır. Planı (giriş, stop, hedef) okur, dört limite
  (işlem başı azami zarar, pozisyon üst sınırı, azami emir, tampon sonrası
  nakit) sığan lot sayısını bulur, hangi limitin belirlediğini söyler ve TEK
  bir bracket emri yazar -> trader/orders.json. Midas kesirli lot verdiği için
  ondalık lot da hesaplar (--whole ile tam lot). Stop azami zarara göre çok
  uzaksa düz bir REDdir, küçük emir değil. Hiçbir şey yerleştirilmez. "kaç lot",
  "ne kadar alayım", "2000 TL'm var", "işlem başı 40 TL riske gireyim",
  "pozisyonu boyutlandır" dendiğinde ya da bist-exit plan yazdıktan sonra kullan.
argument-hint: "[--account 2000] [--max-loss 40] [--whole]"
---

# bist-budget

Lotu matematikle belirler: önce işlem başı azami zarara, sonra nakit/pozisyon
sınırlarına sığdırır. `trader/config.json` varsa oradan okur, yoksa makul
varsayımlar (2000 TL hesap, 40 TL azami zarar, %60 pozisyon sınırı, %10 nakit
tamponu, kesirli açık).

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/size.py"                         # config/plan'dan
python3 "${CLAUDE_SKILL_DIR}/size.py" --account 2000 --max-loss 40
python3 "${CLAUDE_SKILL_DIR}/size.py" --whole                 # kesirli yerine tam lot
python3 "${CLAUDE_SKILL_DIR}/size.py" --json
```

- `trader/plan.json` okur, `trader/orders.json` yazar (bracket: giriş, stop, hedef).
- Config alanları: `account_tl, max_loss_tl, position_cap_pct, max_order_tl,
  cash_buffer_pct, fractional`.
- Midas kesirli lot verir: varsayılan `fractional: true`, lot 2 ondalık.
