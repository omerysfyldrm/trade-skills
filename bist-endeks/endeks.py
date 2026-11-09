#!/usr/bin/env python3
"""bist-endeks — Piyasa Rejimi / Genişlik (BIST).

Gün içi işlemde yönün rüzgârı: XU100 endeksinin 20/50 günlük ortalamaya göre
duruşu ve günlük değişimi, USD/TRY bağlamı ve (opsiyonel) BIST-100'den bir
örneklemde bugün kaç hisse yükselişte (genişlik). Risk-açık / risk-kapalı
tek satır yargı verir. İşlem gününün başında, bist-scanner'dan önce bak.

Not: Endeks sembolü Yahoo'da 'XU100.IS'. Gelmezse '^XU100' denenir.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402


def sma(v, n):
    return sum(v[-n:]) / n if len(v) >= n else None


def index_snapshot():
    for sym in ("XU100.IS", "^XU100", "XU030.IS"):
        bars = B.candles(sym, "3mo", "1d")
        if len(bars) >= 20:
            return sym, bars
    return None, []


def main():
    p = argparse.ArgumentParser(description="bist-endeks")
    p.add_argument("--breadth", type=int, default=0,
                   help="genişlik için örneklem büyüklüğü (0 = atla)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    sym, bars = index_snapshot()
    out = {"market": B.market_state(), "as_of": B.now_ist().strftime("%Y-%m-%d %H:%M")}
    if not bars:
        print("Endeks verisi alınamadı.", file=sys.stderr); return 1
    closes = [b["c"] for b in bars]
    last, prev = closes[-1], closes[-2]
    ma20, ma50 = sma(closes, 20), sma(closes, 50)
    day = (last - prev) / prev * 100
    regime = "risk-açık" if (ma20 and last > ma20) else "risk-kapalı"
    out["index"] = {"symbol": sym, "last": round(last, 2),
                    "day_pct": round(day, 2),
                    "ma20": round(ma20, 2) if ma20 else None,
                    "ma50": round(ma50, 2) if ma50 else None,
                    "regime": regime}

    usd = B.last_price("USDTRY=X")
    if usd.get("price"):
        out["usdtry"] = {"price": round(usd["price"], 4),
                         "day_pct": round(usd["pct"], 2) if usd.get("pct") is not None else None}

    if args.breadth:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                            "bist-scanner", "bist100.txt")
        syms = []
        if os.path.exists(base):
            syms = [l.split("|")[0].strip() for l in open(base, encoding="utf-8")
                    if l.strip()][:args.breadth]
        up = down = 0
        for s in syms:
            lp = B.last_price(s)
            if lp.get("pct") is None:
                continue
            up += lp["pct"] > 0; down += lp["pct"] <= 0
        out["breadth"] = {"sample": up + down, "up": up, "down": down}

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    ix = out["index"]
    print(f"BIST Rejimi — {out['as_of']} (borsa: {out['market']})")
    print(f"  {ix['symbol']}: {ix['last']}  gün {ix['day_pct']:+.2f}%  "
          f"| 20g {ix['ma20']}  50g {ix['ma50']}")
    print(f"  Rejim: {ix['regime'].upper()}  "
          f"({'endeks 20g ortalamanın üstünde' if ix['regime']=='risk-açık' else 'endeks 20g ortalamanın altında'})")
    if "usdtry" in out:
        print(f"  USD/TRY: {out['usdtry']['price']}  gün {out['usdtry'].get('day_pct','?')}%")
    if "breadth" in out:
        b = out["breadth"]
        print(f"  Genişlik (örneklem {b['sample']}): {b['up']} yükselen / {b['down']} düşen")
    print("  " + ("Rüzgâr arkada; long ORB kurulumları daha güvenli."
                  if ix["regime"] == "risk-açık"
                  else "Rüzgâr karşıda; long kırılımlar daha çok tuzağa düşer, dikkat."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
