"""parsetr — Türkçe sayı ve yapıştırılan tablo ayrıştırma yardımcıları.

Türk biçimi: nokta binlik ayracı, virgül ondalık (1.234.567,89).
Midas/İş Yatırım/Matriks kopyalarındaki satırları toleranslı okur.
"""
import re

# Sayı gövdesi: rakam + nokta (binlik) + opsiyonel virgül ondalık.
# Boşluk DAHİL DEĞİL — boşluk sütun ayracıdır, ayrı sayıları birleştirmez.
_NUM = re.compile(r"-?\d[\d.]*(?:,\d+)?")


def tr_num(s: str):
    """'1.234.567,89' -> 1234567.89 ; '%12,3' -> 12.3 ; başarısızsa None."""
    if s is None:
        return None
    s = s.strip().replace("%", "").replace(" ", "")
    if not s:
        return None
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def nums_in(line: str):
    """Satırdaki tüm sayıları (float) soldan sağa döner."""
    out = []
    for m in _NUM.findall(line):
        v = tr_num(m)
        if v is not None:
            out.append(v)
    return out


def broker_rows(text: str):
    """Aracı kurum dağılımı / takas tablosu.

    Her satırda bir kurum adı + sayılar olduğunu varsayar. En yaygın biçimler:
      AD  ALIS(adet)  SATIS(adet)  [NET]
      AD  NET(adet)
      AD  ALIS_TL  SATIS_TL  NET_TL
    Dönen: [{name, buy, sell, net}] (eldeki kadarıyla).
    """
    rows = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        nums = nums_in(line)
        if not nums:
            continue
        # ad = ilk sayıdan önceki metin
        m = _NUM.search(line)
        name = line[:m.start()].strip(" .:-\t|") if m else line
        if not name or len(name) < 2:
            continue
        buy = sell = net = None
        if len(nums) >= 3:
            buy, sell, net = nums[0], nums[1], nums[2]
        elif len(nums) == 2:
            buy, sell = nums[0], nums[1]
            net = buy - sell
        elif len(nums) == 1:
            net = nums[0]
        rows.append({"name": name, "buy": buy, "sell": sell, "net": net})
    return rows


def depth_rows(text: str):
    """Derinlik (kademe) tablosu. İki yaygın biçim:
      1) 'FIYAT ADET' çiftleri (alış ve satış ayrı bloklar)
      2) 'ALIS_ADET ALIS_FIYAT SATIS_FIYAT SATIS_ADET' (5 kademe ladder)
    Dönen: {'bids': [(fiyat,adet)], 'asks': [(fiyat,adet)]} (tahmini).
    Belirsizse ham satır sayılarını döndürür; yorumlamayı Claude yapar.
    """
    bids, asks, generic = [], [], []
    for raw in text.splitlines():
        nums = nums_in(raw)
        if len(nums) == 4:
            # alis_adet alis_fiyat | satis_fiyat satis_adet
            bids.append((nums[1], nums[0]))
            asks.append((nums[2], nums[3]))
        elif len(nums) == 2:
            generic.append((nums[0], nums[1]))  # (fiyat, adet) ya da tersi
    return {"bids": bids, "asks": asks, "generic": generic}
