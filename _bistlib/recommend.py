"""recommend — piyasadan bağımsız çok-zaman-dilimli öneri motoru.

classify(daily_bars, weekly_bars, monthly_bars) -> her kova için {score, reasons}.
Kovalar: gun_ici, haftalik, aylik, yillik. Puan 0-100, şeffaf kurallardan.
Tahmin değil; teknik tarama. Temel/haber gerekçesini çağıran ekler.
"""
from __future__ import annotations
import indicators as I


def _score(signals):
    """signals: [(ok:bool, weight:int, reason:str)]. Dönen: (0-100, [reasons])."""
    tot = sum(w for _, w, _ in signals)
    got = sum(w for ok, w, _ in signals if ok)
    reasons = [r for ok, _, r in signals if ok]
    return (round(got / tot * 100) if tot else 0), reasons


def classify(daily_bars, weekly_bars=None, monthly_bars=None):
    d = I.summarize(daily_bars) if len(daily_bars) >= 30 else None
    w = I.summarize(weekly_bars) if weekly_bars and len(weekly_bars) >= 15 else None
    m = I.summarize(monthly_bars) if monthly_bars and len(monthly_bars) >= 10 else None
    if not d:
        return {}
    closes = [b["c"] for b in daily_bars]
    last = closes[-1]
    out = {}

    # --- GÜN İÇİ: momentum + 20g zirveye yakınlık + hacim ---
    near_high = (last >= max(closes[-20:-1]) * 0.995) if len(closes) >= 21 else False
    sig = [
        (last > (d["sma20"] or 1e18), 2, "fiyat 20g ortalama üstünde"),
        (near_high, 3, "20 günlük zirveye kırılım/çok yakın"),
        ((d["vol_trend"] or 0) > 1.2, 2, "hacim son 5g > 20g (ilgi artıyor)"),
        (40 <= (d["rsi14"] or 50) <= 75, 1, "RSI aşırı değil"),
        ((d["mom20_pct"] or 0) > 2, 1, "20g momentum pozitif"),
    ]
    out["gun_ici"] = dict(zip(("score", "reasons"), _score(sig)))

    # --- HAFTALIK (swing): yukarı trend + aşırı alımda değil + ortalama üstü ---
    sig = [
        (d["trend"] in ("yukarı", "güçlü-yukarı"), 3, f"günlük trend {d['trend']}"),
        (last > (d["sma50"] or 1e18), 2, "fiyat 50g ortalama üstünde"),
        (45 <= (d["rsi14"] or 50) <= 68, 2, "RSI sağlıklı bölgede (parabolik değil)"),
        ((d["mom20_pct"] or 0) > 0, 1, "20g momentum pozitif"),
        (-12 <= (d["from_high_pct"] or -99) <= 0, 2, "52h zirveye yakın (güç)"),
    ]
    out["haftalik"] = dict(zip(("score", "reasons"), _score(sig)))

    # --- AYLIK (pozisyon): haftalık trend + 200g üstü + momentum ---
    w_up = bool(w and w["last"] and w["sma20"] and w["last"] > w["sma20"])
    sig = [
        (bool(d["sma200"]) and last > (d["sma200"] or 1e18), 3, "fiyat 200g ortalama üstünde (ana trend yukarı)"),
        (w_up, 2, "haftalık grafik 20 ortalaması üstünde"),
        (d["cross_50_200"] == "golden", 2, "50/200 golden cross (yeni)"),
        ((d["from_low_pct"] or 0) > 20, 1, "52h dipten belirgin uzakta"),
        ((w and (w["mom20_pct"] or 0) > 0) or False, 1, "haftalık momentum pozitif"),
    ]
    out["aylik"] = dict(zip(("score", "reasons"), _score(sig)))

    # --- YILLIK (uzun vade): aylık trend + uzun ortalama üstü + sağlık ---
    m_up = bool(m and m["last"] and m["sma20"] and m["last"] > m["sma20"])
    sig = [
        (bool(d["sma200"]) and last > (d["sma200"] or 1e18) * 1.02, 3, "200g ortalamanın belirgin üstünde"),
        (m_up, 3, "aylık grafik uzun ortalaması üstünde (uzun vade boğa)"),
        (d["cross_50_200"] != "death", 1, "ölüm kesişimi yok"),
        ((d["from_low_pct"] or 0) > 40, 2, "uzun vadeli taban çok gerilerde (yükselen seri)"),
        (30 <= (d["rsi14"] or 50) <= 70, 1, "aşırı alım/satım uçlarında değil"),
    ]
    out["yillik"] = dict(zip(("score", "reasons"), _score(sig)))

    out["_ind"] = {"daily": d, "weekly": w, "monthly": m}
    return out


BUCKET_TR = {"gun_ici": "Gün içi", "haftalik": "Haftalık",
             "aylik": "Aylık", "yillik": "Yıllık"}
