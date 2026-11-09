#!/usr/bin/env python3
"""bist-risk — Risk Yöneticisi (TL).

Her emri limitlerine karşı denetler ve aşanı broker'a GİTMEDEN durdurur:
stop zorunlu, stop'taki zarar işlem başı azami zarara sığmalı, R:R asgariyi
geçmeli, günün toplam riski günlük zarar limitine sığmalı, günlük işlem sayısı
aşılmamalı, giriş penceresi dışında/borsa kapalıyken yeni giriş yok. PASS ya
da BLOCK, gerekçesiyle. Verdiği kararı trader/risk_verdict.json'a yazar;
bist-broker sadece PASS almış emri gösterir.
"""
import argparse, json, os, sys, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402

DEFAULTS = {"max_loss_tl": 40, "daily_loss_limit_tl": 80, "max_trades_per_day": 3,
            "min_rr": 1.5, "entry_window": ["10:00", "13:00"], "account_tl": 2000,
            "position_cap_pct": 60}


def load_cfg():
    cfg = dict(DEFAULTS)
    pf = os.path.join("trader", "config.json")
    if os.path.exists(pf):
        try:
            cfg.update(json.load(open(pf, encoding="utf-8")))
        except Exception:                            # noqa: BLE001
            pass
    return cfg


def trades_today():
    jf = os.path.join("trader", "journal.jsonl")
    if not os.path.exists(jf):
        return 0, 0.0
    today = B.now_ist().date().isoformat()
    n, risked = 0, 0.0
    for line in open(jf, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:                            # noqa: BLE001
            continue
        if r.get("date") == today:
            n += 1
            risked += r.get("max_loss_tl", 0)
    return n, risked


def main():
    p = argparse.ArgumentParser(description="bist-risk")
    p.add_argument("--now")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    cfg = load_cfg()

    of = os.path.join("trader", "orders.json")
    if not os.path.exists(of):
        print("Emir yok: önce bist-budget.", file=sys.stderr); return 1
    o = json.load(open(of, encoding="utf-8"))
    plan = json.load(open(os.path.join("trader", "plan.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join("trader", "plan.json")) else {}

    when = dt.datetime.fromisoformat(args.now).replace(tzinfo=B.IST) if args.now else B.now_ist()
    fails = []

    # stop zorunlu
    if not o.get("stop_loss") or o["stop_loss"] >= o["limit_price"]:
        fails.append("Stop yok ya da girişin üstünde.")
    # azami zarar
    if o.get("max_loss_tl", 1e9) > cfg["max_loss_tl"] + 0.01:
        fails.append(f"Stop'taki zarar {o['max_loss_tl']} TL > azami {cfg['max_loss_tl']} TL.")
    # R:R
    rr = plan.get("rr", 0)
    if rr < cfg["min_rr"]:
        fails.append(f"R:R {rr} < asgari {cfg['min_rr']}.")
    # günlük
    n, risked = trades_today()
    if n >= cfg["max_trades_per_day"]:
        fails.append(f"Günlük işlem sınırı dolu ({n}/{cfg['max_trades_per_day']}).")
    if risked + o.get("max_loss_tl", 0) > cfg["daily_loss_limit_tl"] + 0.01:
        fails.append(f"Günlük risk {risked + o.get('max_loss_tl',0):.0f} TL > "
                     f"limit {cfg['daily_loss_limit_tl']} TL.")
    # pozisyon üst sınırı
    cap = cfg["account_tl"] * cfg["position_cap_pct"] / 100
    if o.get("est_cost_tl", 0) > cap + 0.01:
        fails.append(f"Pozisyon {o['est_cost_tl']:.0f} TL > sınır {cap:.0f} TL.")
    # giriş penceresi + borsa açık mı
    w0 = dt.datetime.strptime(cfg["entry_window"][0], "%H:%M").time()
    w1 = dt.datetime.strptime(cfg["entry_window"][1], "%H:%M").time()
    state = B.market_state(when)
    if args.now is None and state != "acik":
        fails.append(f"Borsa {state}; yeni giriş yok. (Çıkış her zaman serbest.)")
    elif not (w0 <= when.time() <= w1):
        fails.append(f"Saat {when:%H:%M} giriş penceresi dışında "
                     f"({cfg['entry_window'][0]}–{cfg['entry_window'][1]}).")

    verdict = "BLOCK" if fails else "PASS"
    out = {"verdict": verdict, "symbol": o["symbol"], "reasons": fails,
           "order_fingerprint": f"{o['symbol']}:{o['limit_price']}:{o['stop_loss']}:{o['qty']}",
           "checked_at": when.isoformat(timespec="minutes")}
    os.makedirs("trader", exist_ok=True)
    json.dump(out, open(os.path.join("trader", "risk_verdict.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0 if verdict == "PASS" else 2

    print(f"{o['symbol']} — RİSK: {verdict}")
    if fails:
        for r in fails:
            print(f"  ✗ {r}")
        print("  Emir broker'a gitmez.")
    else:
        print(f"  ✓ Tüm kurallar geçti. Günlük: {n}/{cfg['max_trades_per_day']} işlem, "
              f"{risked:.0f}/{cfg['daily_loss_limit_tl']:.0f} TL risk kullanıldı.")
        print("  Sıradaki: bist-broker (elle Midas emri).")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
