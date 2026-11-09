# trade-skills — BIST / ABD / Kripto tarama ve öneri skilleri

Kişisel kullanım. Yahoo Finance (fiyat) + Google News (haber/KAP) üzerinden
çok-zaman-dilimli hisse/coin taraması, teknik (SMA/EMA/RSI/momentum/cross) +
temel (haber/katalizör) gerekçeyle. **Alım-satımı kullanıcı yapar; emir yok.**

## Ana komutlar
```
python3 bist-oneri/oneri.py         # BIST: gün içi/haftalık/aylık/yıllık öneri
python3 kripto-oneri/kripto.py      # Kripto (7/24)
python3 us-oneri/us.py              # ABD borsası
python3 piyasa-duygu/duygu.py       # Makro/lider haber duygu analizi
```
Ortak veri/gösterge katmanı `_bistlib/`. Yatırım tavsiyesi değildir.
