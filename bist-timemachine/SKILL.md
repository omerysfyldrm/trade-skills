---
name: bist-timemachine
description: >-
  BIST Zaman Makinesi. Bir işlemin olası sonuçlarını riske girmeden önce
  oynatır: planı (giriş, stop, hedef) alır, günün geri kalanını hissenin KENDİ
  son 60 günlük 5 dakikalık barlarından 10.000 kez yeniden kurar ve aynı açılış
  aralığı kuralını her geçmiş günde tekrar koşturur. Hedef-önce, stop-önce,
  ne-ikisi olasılığını, kapanıştaki ortalama R'yi, geçmişi ve tek bir dürüst
  yargıyı basar. Deterministik (seed). "zaman makinesini çalıştır", "bu işlemi
  oynat", "olasılık ne", "simüle et", "monte carlo", "backtest", "yazı-tura mı"
  dendiğinde ya da bist-exit plan yazdıktan sonra, bist-budget'tan önce kullan.
argument-hint: "[--n 10000] [--seed 19]"
---

# bist-timemachine

Bir dolar riske atmadan önce dürüst oranı gösterir. İki yöntem: hissenin kendi
5dk getirilerinden Monte Carlo simülasyonu + aynı kuralın geçmiş günlerdeki
gerçek sonucu.

`${CLAUDE_SKILL_DIR}` bu skilin klasörüdür.

```bash
python3 "${CLAUDE_SKILL_DIR}/timemachine.py"                 # plan.json'dan
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" --n 20000 --seed 7
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" --json
```

- `trader/plan.json`'ı okur (bist-exit yazar).
- Çıktı: hedef/stop/ne-ikisi olasılığı, ortalama R, geçmişte kaç kez tetiklendi
  ve nasıl sonuçlandı, tek satır yargı.
- Amaç kehanet değil, beklentini gerçek verinin önünde sınamak. Çoğu ORB
  kurulumu yazı-turaya yakın çıkar; mesele budur.
