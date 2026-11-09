---
name: bist-endeks
description: >-
  BIST Piyasa Rejimi / Genişlik. Gün içi işlemde yönün rüzgârını gösterir:
  XU100 endeksinin 20/50 günlük ortalamaya göre duruşu ve günlük değişimi,
  USD/TRY bağlamı ve (opsiyonel) BIST-100'den bir örneklemde bugün kaç hisse
  yükselişte (genişlik). Risk-açık / risk-kapalı tek satır yargı verir. "piyasa
  nasıl", "endeks ne durumda", "XU100 nerede", "risk açık mı", "bugün alım
  günü mü", "piyasa rejimi", "genişlik" dendiğinde ya da işlem gününün başında
  bist-scanner'dan önce kullan.
argument-hint: "[--breadth 30]"
---

# bist-endeks

Tek tek hisseye girmeden önce genel rüzgâr: endeks ortalamasının üstünde mi
(risk-açık) altında mı (risk-kapalı), USD/TRY ne yönde, piyasa genişliği nasıl.
Long ORB kurulumları risk-açık rejimde daha güvenilir, risk-kapalıda daha çok
tuzağa düşer.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/endeks.py"                 # XU100 rejimi + USD/TRY
python3 "${CLAUDE_SKILL_DIR}/endeks.py" --breadth 30    # +30 hisselik genişlik örneklemi
python3 "${CLAUDE_SKILL_DIR}/endeks.py" --json
```

- Endeks sembolü Yahoo'da `XU100.IS` (gelmezse `^XU100`, sonra `XU030.IS`).
- `--breadth N` için `bist-scanner/bist100.txt`'ten ilk N hisseyi örnekler
  (her biri bir istek; büyük N yavaştır).
