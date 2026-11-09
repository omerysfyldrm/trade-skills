#!/usr/bin/env python3
"""bist-alerts — Fiyat Alarmları (BIST).

Plandan üç alarmı tek seferde kurar (stop, hedef ve 'gün sonu düz' saati),
ayrıca --above/--below ile elle seviye ve açılış zili. Borsa İstanbul saatlerini
(10:00–18:00, 2026-2027 tatilleri) bilir, İstanbul saatini kendi hesaplar,
Yahoo'dan gecikmeli fiyat çeker ve 'plan' modunda şu an hangi seviyenin çalmış
olduğunu söyler.
"""
import argparse, json, os, sys, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="bist-alerts")
    p.add_argument("symbol", nargs="?")
    p.add_argument("--above", type=float)
    p.add_argument("--below", type=float)
    p.add_argument("--from-plan", action="store_true", help="plan.json'dan stop/hedef/kapanış")
    p.add_argument("--check", action="store_true", help="şu an fiyatı çek, çalanı bildir")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    plan = json.load(open(os.path.join("trader", "plan.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join("trader", "plan.json")) else {}
    sym = (args.symbol or plan.get("symbol") or "").upper()
    if not sym:
        print("Hisse ver: bist-alerts THYAO --above 310", file=sys.stderr); return 1

    alerts = []
    if args.from_plan and plan:
        alerts += [{"type": "stop", "level": plan["stop"], "dir": "below"},
                   {"type": "hedef", "level": plan["target"], "dir": "above"},
                   {"type": "gun-sonu", "time": plan.get("flat_by", "17:55")}]
    if args.above:
        alerts.append({"type": "elle", "level": args.above, "dir": "above"})
    if args.below:
        alerts.append({"type": "elle", "level": args.below, "dir": "below"})
    if not alerts:
        print("Alarm yok. --from-plan ya da --above/--below ver.", file=sys.stderr); return 1

    now = B.now_ist()
    state = B.market_state(now)
    rung = []
    price = None
    if args.check:
        lp = B.last_price(sym)
        price = lp.get("price")
        for a in alerts:
            if "level" in a and price is not None:
                if a["dir"] == "above" and price >= a["level"]:
                    rung.append(a)
                if a["dir"] == "below" and price <= a["level"]:
                    rung.append(a)

    out = {"symbol": sym, "market": state, "now": now.strftime("%H:%M"),
           "price": price, "alerts": alerts, "rung": rung}
    os.makedirs("trader", exist_ok=True)
    json.dump(out, open(os.path.join("trader", "alerts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    print(f"{sym} alarmları — {now:%H:%M} İstanbul (borsa: {state})")
    for a in alerts:
        if "level" in a:
            print(f"  • {a['type']}: {a['dir']} {a['level']} TL")
        else:
            print(f"  • {a['type']}: {a['time']}")
    if args.check:
        print(f"  Şu an fiyat: {price} TL")
        if rung:
            for a in rung:
                print(f"  🔔 ÇALDI — {a['type']} ({a['dir']} {a['level']})")
        else:
            print("  Henüz çalan yok.")
    else:
        print("  (Şu anki fiyata göre kontrol için --check ekle.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
