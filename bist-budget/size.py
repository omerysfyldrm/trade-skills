#!/usr/bin/env python3
"""bist-budget — Bütçe Yöneticisi (TL).

Planı (giriş, stop, hedef) okur ve dört limite sığan lot sayısını bulur:
işlem başına azami zarar, pozisyon üst sınırı, azami emir, tampon sonrası
nakit. Hangi limitin belirlediğini söyler ve TEK bir bracket emri yazar
(giriş, stop-loss, take-profit) -> trader/orders.json. Midas kesirli lot
verdiği için --fractional ile ondalık lot da hesaplar. Stop, azami zarara
göre çok uzaksa düz bir REDdir, küçük emir değil. Hiçbir şey yerleştirilmez.
"""
import argparse, json, os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402

DEFAULTS = {"account_tl": 2000, "max_loss_tl": 40, "position_cap_pct": 60,
            "max_order_tl": 0, "cash_buffer_pct": 10, "fractional": True}


def load_cfg():
    cfg = dict(DEFAULTS)
    pf = os.path.join("trader", "config.json")
    if os.path.exists(pf):
        try:
            cfg.update(json.load(open(pf, encoding="utf-8")))
        except Exception:                            # noqa: BLE001
            pass
    return cfg


def main():
    p = argparse.ArgumentParser(description="bist-budget")
    p.add_argument("--account", type=float)
    p.add_argument("--max-loss", type=float, help="işlem başı azami zarar TL")
    p.add_argument("--fractional", dest="fractional", action="store_true")
    p.add_argument("--whole", dest="fractional", action="store_false")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fractional=None)
    args = p.parse_args()

    cfg = load_cfg()
    if args.account:
        cfg["account_tl"] = args.account
    if args.max_loss:
        cfg["max_loss_tl"] = args.max_loss
    if args.fractional is not None:
        cfg["fractional"] = args.fractional

    pf = os.path.join("trader", "plan.json")
    if not os.path.exists(pf):
        print("Plan yok: önce bist-exit.", file=sys.stderr); return 1
    plan = json.load(open(pf, encoding="utf-8"))
    entry, stop, target = plan["entry"], plan["stop"], plan["target"]
    risk = entry - stop
    if risk <= 0:
        print("Geçersiz plan: stop >= giriş.", file=sys.stderr); return 1

    acct = cfg["account_tl"]
    cash = acct * (1 - cfg["cash_buffer_pct"] / 100)
    pos_cap = acct * cfg["position_cap_pct"] / 100
    max_order = cfg["max_order_tl"] or pos_cap

    # her limitten gelen lot
    by_loss = cfg["max_loss_tl"] / risk
    by_cash = cash / entry
    by_cap = pos_cap / entry
    by_order = max_order / entry
    raw = min(by_loss, by_cash, by_cap, by_order)
    which = min([("azami zarar", by_loss), ("nakit", by_cash),
                 ("pozisyon sınırı", by_cap), ("azami emir", by_order)],
                key=lambda x: x[1])[0]

    if cfg["fractional"]:
        qty = math.floor(raw * 100) / 100     # 2 ondalık (Midas kesirli)
    else:
        qty = math.floor(raw)

    if qty <= 0:
        print(f"RED: {cfg['max_loss_tl']} TL azami zararla bu stop'ta "
              f"(hisse başı {risk:.2f} TL risk) pozisyon sığmıyor. "
              f"Daha dar stoplu bir kurulum ya da daha büyük hesap gerek.",
              file=sys.stderr)
        return 1

    cost = qty * entry
    loss_at_stop = qty * risk
    gain_at_target = qty * (target - entry)
    order = {"symbol": plan["symbol"], "side": "buy", "qty": qty,
             "type": "bracket", "limit_price": entry,
             "stop_loss": stop, "take_profit": target,
             "est_cost_tl": round(cost, 2), "max_loss_tl": round(loss_at_stop, 2),
             "target_gain_tl": round(gain_at_target, 2),
             "decided_by": which, "fractional": cfg["fractional"],
             "flat_by": plan.get("flat_by", "17:55"),
             "as_of": B.now_ist().isoformat(timespec="minutes")}
    os.makedirs("trader", exist_ok=True)
    json.dump(order, open(os.path.join("trader", "orders.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if args.json:
        print(json.dumps(order, ensure_ascii=False, indent=2)); return 0

    print(f"{plan['symbol']} — Bütçe ({acct:.0f} TL hesap, {cfg['max_loss_tl']:.0f} TL azami zarar)")
    print(f"  Lot      : {qty}{'  (kesirli)' if cfg['fractional'] else ''}  — sınırı belirleyen: {which}")
    print(f"  Maliyet  : {cost:,.2f} TL")
    print(f"  Stop'ta  : -{loss_at_stop:,.2f} TL")
    print(f"  Hedefte  : +{gain_at_target:,.2f} TL")
    print(f"  Emir     : AL {qty} {plan['symbol']}  stop {stop}  hedef {target}")
    print("  Sıradaki: bist-risk (kural denetimi).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
