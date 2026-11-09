#!/usr/bin/env python3
"""bist-timemachine — Zaman Makinesi.

Bir dolar riske atmadan önce işlemin günün geri kalanını N kez (varsayılan
10.000) hissenin KENDİ son ~60 günlük 5 dakikalık barlarından yeniden kurar
ve aynı ORB kuralını her geçmiş günde tekrar koşturur. Hedef-önce, stop-önce,
ne-ikisi olasılıklarını, kapanıştaki ortalama R'yi, geçmişi ve tek bir dürüst
yargıyı basar. plan.json'dan okur. Emir YERLEŞTİRMEZ.

Deterministik: --seed ile herkes aynı sonucu üretir.
"""
import argparse, json, os, sys, random, statistics as st, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402


def intraday_by_day(sym):
    """{date: [5m bar,...]} son ~60 gün."""
    bars = B.candles(sym, "60d", "5m")
    days = {}
    for b in bars:
        d = dt.datetime.fromtimestamp(b["t"], B.IST).date()
        days.setdefault(d, []).append(b)
    return days


def five_min_returns(days):
    rets = []
    for d, bs in days.items():
        for i in range(1, len(bs)):
            pc = bs[i - 1]["c"]
            if pc:
                rets.append(bs[i]["c"] / pc - 1.0)
    return rets


def simulate(entry, stop, target, rets, bars_left, n, seed):
    rnd = random.Random(seed)
    tgt_first = stop_first = neither = 0
    rr = (target - entry) / (entry - stop)
    end_R = []
    for _ in range(n):
        price = entry
        hit = None
        for _ in range(bars_left):
            price *= (1 + rnd.choice(rets))
            if price <= stop:
                hit = "stop"; break
            if price >= target:
                hit = "target"; break
        if hit == "target":
            tgt_first += 1; end_R.append(rr)
        elif hit == "stop":
            stop_first += 1; end_R.append(-1.0)
        else:
            neither += 1
            end_R.append((price - entry) / (entry - stop))
    return tgt_first, stop_first, neither, end_R


def backtest(days, or_minutes=15):
    """Her geçmiş günde ORB kuralı: aralık kır, 1R stop / 2R hedef, hangisi önce."""
    fired = hit_t = hit_s = neither = 0
    for d, bs in sorted(days.items()):
        if len(bs) < 6:
            continue
        o = dt.datetime.combine(d, dt.time(B.OPEN_H, B.OPEN_M), B.IST)
        end = o + dt.timedelta(minutes=or_minutes)
        rb = [b for b in bs if o <= dt.datetime.fromtimestamp(b["t"], B.IST) < end]
        if not rb:
            continue
        rhigh = max(b["h"] for b in rb); rlow = min(b["l"] for b in rb)
        after = [b for b in bs if dt.datetime.fromtimestamp(b["t"], B.IST) >= end]
        trig = next((b for b in after if b["c"] > rhigh), None)
        if not trig:
            continue
        entry = trig["c"]; stop = (rhigh + rlow) / 2
        if stop >= entry:
            continue
        risk = entry - stop; target = entry + 2 * risk
        fired += 1
        seq = after[after.index(trig) + 1:]
        res = "neither"
        for b in seq:
            if b["l"] <= stop:
                res = "stop"; break
            if b["h"] >= target:
                res = "target"; break
        hit_t += res == "target"; hit_s += res == "stop"; neither += res == "neither"
    return fired, hit_t, hit_s, neither


def main():
    p = argparse.ArgumentParser(description="bist-timemachine")
    p.add_argument("--n", type=int, default=10000)
    p.add_argument("--seed", type=int, default=19)
    p.add_argument("--bars-left", type=int, default=60, help="kapanışa kalan 5dk bar")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    pf = os.path.join("trader", "plan.json")
    if not os.path.exists(pf):
        print("Plan yok: önce bist-exit.", file=sys.stderr); return 1
    plan = json.load(open(pf, encoding="utf-8"))
    sym, entry, stop, target = plan["symbol"], plan["entry"], plan["stop"], plan["target"]

    days = intraday_by_day(sym)
    rets = five_min_returns(days)
    if len(rets) < 100:
        print(f"{sym}: simülasyon için yeterli 5dk veri yok ({len(rets)}).", file=sys.stderr); return 1

    tf, sf, nf, endR = simulate(entry, stop, target, rets, args.bars_left, args.n, args.seed)
    fired, ht, hs, nn = backtest(days)
    avgR = st.mean(endR)

    p_t = tf / args.n * 100; p_s = sf / args.n * 100; p_n = nf / args.n * 100
    out = {"symbol": sym, "entry": entry, "stop": stop, "target": target,
           "sim": {"n": args.n, "seed": args.seed, "target_first_pct": round(p_t, 1),
                   "stop_first_pct": round(p_s, 1), "neither_pct": round(p_n, 1),
                   "avg_R": round(avgR, 2)},
           "backtest": {"fired": fired, "target": ht, "stop": hs, "neither": nn}}

    # dürüst yargı
    if p_t >= p_s + 10 and avgR > 0.15:
        verdict = "Olasılık hafif lehte — yine de küçük riskle."
    elif abs(p_t - p_s) < 8:
        verdict = "Yazı-tura. Beklenti düşük; bu kurulumda kenarın yok."
    else:
        verdict = "Olasılık aleyhte. Bu işlemi geçmek mantıklı."

    if args.json:
        out["verdict"] = verdict
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    print(f"{sym} — Zaman Makinesi ({args.n:,} simülasyon, seed {args.seed})")
    print(f"  Giriş {entry} / Stop {stop} / Hedef {target}  (R:R {plan['rr']})")
    print(f"  Hedef önce : {p_t:.1f}%")
    print(f"  Stop önce  : {p_s:.1f}%")
    print(f"  Kapanışta açık: {p_n:.1f}%   | ortalama sonuç: {avgR:+.2f}R")
    if fired:
        print(f"  Geçmiş: aynı kural 60 günde {fired} kez tetiklendi — "
              f"{ht} hedef, {hs} stop, {nn} ne ikisi.")
    else:
        print("  Geçmiş: bu kural son 60 günde hiç tetiklenmemiş (az örnek).")
    print(f"  Yargı: {verdict}")
    print("  Sıradaki: bist-budget (lot) -> bist-risk (kurallar).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
