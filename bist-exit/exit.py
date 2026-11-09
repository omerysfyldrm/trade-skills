#!/usr/bin/env python3
"""bist-exit — Çıkış Planlayıcı (long).

Girişten ÖNCE stop ve hedefi belirler. Stop varsayılan: açılış aralığının
orta noktası (ya da aralık düşüğü / --pct / --atr katı / --stop). Hedef: 2R
(ya da --rr katı / --target). Kuruşa yuvarlar. Girişten yüksek/eşit stop,
girişten düşük/eşit hedef ya da spread'e sığmayacak kadar dar stop'u reddeder.
trader/plan.json yazar (timemachine, budget, alerts okur). Emir YERLEŞTİRMEZ.
"""
import argparse, json, os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402


def round_cent(x, down=True):
    f = math.floor if down else math.ceil
    return f(x * 100) / 100


def atr(bars, n=14):
    if len(bars) < n + 1:
        return None
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = bars[i]["h"], bars[i]["l"], bars[i - 1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs[-n:]) / n


def main():
    p = argparse.ArgumentParser(description="bist-exit")
    p.add_argument("symbol", nargs="?")
    p.add_argument("--entry", type=float)
    p.add_argument("--stop", type=float, help="doğrudan stop fiyatı")
    p.add_argument("--stop-mode", choices=["mid", "low", "pct", "atr"], default="mid")
    p.add_argument("--pct", type=float, default=2.0, help="stop-mode pct için %")
    p.add_argument("--atr-mult", type=float, default=1.5)
    p.add_argument("--rr", type=float, default=2.0, help="hedef = giriş + rr*R")
    p.add_argument("--target", type=float)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    e = json.load(open(os.path.join("trader", "entry.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join("trader", "entry.json")) else {}
    sym = (args.symbol or e.get("symbol") or "").upper()
    entry = args.entry or e.get("entry")
    rlow = e.get("range_low")
    rhigh = e.get("range_high")
    if not sym or not entry:
        print("Giriş gerek: önce bist-entry, ya da --symbol X --entry F", file=sys.stderr)
        return 1

    # stop
    if args.stop:
        stop = args.stop
    elif args.stop_mode == "mid" and rlow and rhigh:
        stop = (rlow + rhigh) / 2
    elif args.stop_mode == "low" and rlow:
        stop = rlow
    elif args.stop_mode == "pct":
        stop = entry * (1 - args.pct / 100)
    elif args.stop_mode == "atr":
        a = atr(B.candles(sym, "1mo", "1d"))
        if not a:
            print("ATR için yeterli veri yok.", file=sys.stderr); return 1
        stop = entry - args.atr_mult * a
    else:
        stop = entry * (1 - args.pct / 100)
    stop = round_cent(stop, down=True)

    if stop >= entry:
        print(f"RED: stop ({stop}) girişin ({entry}) altında olmalı.", file=sys.stderr); return 1
    risk = entry - stop
    if risk / entry < 0.003:
        print(f"RED: stop çok dar ({risk/entry*100:.2f}%), spread'e sığmaz.", file=sys.stderr); return 1

    target = args.target if args.target else round_cent(entry + args.rr * risk, down=False)
    if target <= entry:
        print(f"RED: hedef ({target}) girişin üstünde olmalı.", file=sys.stderr); return 1

    plan = {"symbol": sym, "entry": round(entry, 2), "stop": stop,
            "target": round(target, 2), "risk_per_share": round(risk, 2),
            "rr": round((target - entry) / risk, 2),
            "flat_by": "17:55", "as_of": B.now_ist().isoformat(timespec="minutes")}
    os.makedirs("trader", exist_ok=True)
    json.dump(plan, open(os.path.join("trader", "plan.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2)); return 0

    print(f"{sym} çıkış planı:")
    print(f"  Giriş   : {plan['entry']} TL")
    print(f"  Stop    : {plan['stop']} TL   (hisse başı risk {plan['risk_per_share']} TL)")
    print(f"  Hedef   : {plan['target']} TL   (R:R {plan['rr']})")
    print(f"  Kapat   : {plan['flat_by']}'e kadar düz (gün içi)")
    print("  Sıradaki: bist-timemachine (olasılık), sonra bist-budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
