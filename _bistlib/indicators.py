"""indicators — piyasadan bağımsız teknik analiz fonksiyonları.

Hepsi düz OHLC listeleriyle çalışır (BIST, ABD, kripto fark etmez).
bars: [{'o','h','l','c','v'}]. closes: [float].
"""
from __future__ import annotations


def sma(vals, n):
    return sum(vals[-n:]) / n if len(vals) >= n else None


def ema(vals, n):
    if len(vals) < n:
        return None
    k = 2 / (n + 1)
    e = sum(vals[:n]) / n
    for v in vals[n:]:
        e = v * k + e * (1 - k)
    return e


def rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    gains = losses = 0.0
    for i in range(-n, 0):
        d = closes[i] - closes[i - 1]
        gains += max(d, 0)
        losses += max(-d, 0)
    if losses == 0:
        return 100.0
    rs = (gains / n) / (losses / n)
    return 100 - 100 / (1 + rs)


def atr(bars, n=14):
    if len(bars) < n + 1:
        return None
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = bars[i]["h"], bars[i]["l"], bars[i - 1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs[-n:]) / n


def slope_pct(vals, n):
    """Son n barda yüzde eğim (basit): (son - n önce) / n önce."""
    if len(vals) < n + 1 or not vals[-n - 1]:
        return None
    return (vals[-1] - vals[-n - 1]) / vals[-n - 1] * 100


def pct_from_extreme(closes, lookback, kind="high"):
    """52h/52d yüksekten/düşükten uzaklık (%)."""
    if len(closes) < 2:
        return None
    window = closes[-lookback:] if lookback else closes
    ref = max(window) if kind == "high" else min(window)
    if not ref:
        return None
    return (closes[-1] - ref) / ref * 100


def cross(closes, fast, slow):
    """Son barda golden/death cross oldu mu? 'golden'/'death'/None."""
    if len(closes) < slow + 2:
        return None
    f_now, f_prev = sma(closes, fast), sma(closes[:-1], fast)
    s_now, s_prev = sma(closes, slow), sma(closes[:-1], slow)
    if None in (f_now, f_prev, s_now, s_prev):
        return None
    if f_prev <= s_prev and f_now > s_now:
        return "golden"
    if f_prev >= s_prev and f_now < s_now:
        return "death"
    return None


def trend_label(closes):
    """Fiyatın SMA20/50/200 dizilimine göre trend etiketi + gerekçe."""
    last = closes[-1]
    m20, m50, m200 = sma(closes, 20), sma(closes, 50), sma(closes, 200)
    if None in (m20, m50):
        return "yetersiz-veri", []
    reasons = []
    if m200 and last > m20 > m50 > m200:
        return "güçlü-yukarı", ["fiyat > 20>50>200 ortalama (tam dizili boğa)"]
    if last > m20 > m50:
        reasons.append("fiyat > 20 > 50 ortalama (yukarı)")
        return "yukarı", reasons
    if last < m20 < m50:
        return "aşağı", ["fiyat < 20 < 50 ortalama (düşüş)"]
    return "karışık", ["ortalamalar karışık"]


def summarize(bars):
    """Bir zaman dilimi barları için gösterge özeti."""
    closes = [b["c"] for b in bars]
    vols = [b.get("v", 0) for b in bars]
    out = {
        "last": closes[-1] if closes else None,
        "sma20": sma(closes, 20), "sma50": sma(closes, 50), "sma200": sma(closes, 200),
        "ema20": ema(closes, 20),
        "rsi14": rsi(closes, 14),
        "mom20_pct": slope_pct(closes, 20),
        "from_high_pct": pct_from_extreme(closes, 252, "high"),
        "from_low_pct": pct_from_extreme(closes, 252, "low"),
        "cross_50_200": cross(closes, 50, 200),
        "vol_trend": (sma(vols, 5) / sma(vols, 20)) if sma(vols, 20) else None,
    }
    out["trend"], out["trend_reasons"] = trend_label(closes)
    return out
