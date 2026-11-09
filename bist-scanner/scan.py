#!/usr/bin/env python3
"""bist-scanner — BIST grafik tarayıcı.

Alt komutlar:
  universe   Gömülü BIST-100 listesini Yahoo'ya karşı doğrular -> trader/universe.txt
  daily      Günlük kapanışlardan kurulum tarar (önce açılış) -> trader/watchlist.json
  orb        Açılış aralığı kırılımı (bugün, İstanbul 10:00 açılış) -> trader/watchlist.json

Veri: Yahoo .IS chart (TRY). Bir tarama = kurala uyan grafikler listesi,
alınacak hisse listesi DEĞİL. Çoğu gün içi işlemci para kaybeder; tarayıcı
bunu değiştirmez, sadece elle 100 grafik çevirmekten kurtarır.
"""
import argparse, json, os, sys, time, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = "trader"


def _load_universe(path):
    syms = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.split("|")[0].strip().upper()
            if s and not s.startswith("#"):
                syms.append(s)
    return syms


def _write(obj, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# --- setup kuralları (günlük) ---------------------------------------------
def sma(vals, n):
    if len(vals) < n:
        return None
    return sum(vals[-n:]) / n


def analyze_daily(sym, bars):
    """bars: en az ~25 günlük bar. Uyan kurulum adlarını döner."""
    if len(bars) < 21:
        return []
    closes = [b["c"] for b in bars]
    highs = [b["h"] for b in bars]
    lows = [b["l"] for b in bars]
    last = closes[-1]
    hits = []
    ma20 = sma(closes, 20)
    prev20high = max(highs[-21:-1])          # son gün hariç 20 günün en yükseği
    # 1) 20 günlük kapanış-zirvesi kırılımı
    if last >= max(closes[-21:-1]):
        hits.append("20g-zirve-kirilim")
    # 2) 20 günlük ortalamayı geri aldı
    if ma20 and closes[-2] < ma20 <= last:
        hits.append("20g-ort-geri-aldi")
    # 3) boğa bayrağı: son 10 günde sert yükseliş sonrası dar sıkışma
    if len(closes) >= 15:
        run = (closes[-10] - closes[-15]) / closes[-15] if closes[-15] else 0
        rng = (max(highs[-5:]) - min(lows[-5:])) / last if last else 1
        if run > 0.08 and rng < 0.05 and last > ma20:
            hits.append("boga-bayragi")
    # 4) aşırı satım (RSI-benzeri basit): son 7 günde büyük düşüş
    chg7 = (last - closes[-8]) / closes[-8] if len(closes) >= 8 and closes[-8] else 0
    if chg7 < -0.12:
        hits.append("asiri-satim")
    # 5) aşırı satım tepkisi: düşük yapıp yeşil kapanan ilk gün
    if chg7 < -0.10 and last > closes[-2] and bars[-1]["c"] > bars[-1]["o"]:
        hits.append("asiri-satim-tepki")
    return hits


def cmd_universe(args):
    base = _load_universe(args.source or os.path.join(HERE, "bist100.txt"))
    out_path = os.path.join(OUT_DIR, "universe.txt")
    good, dead = [], []
    print(f"{len(base)} sembol Yahoo'ya karşı doğrulanıyor...", file=sys.stderr)
    for s in base:
        lp = B.last_price(s)
        if lp.get("price"):
            good.append(f"{s}|{lp['price']:.2f} TRY")
        else:
            dead.append(s)
        time.sleep(args.pause)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(good) + "\n")
    print(f"{len(good)} canlı sembol -> {out_path}"
          + (f"  (atlanan: {', '.join(dead)})" if dead else ""))
    return 0 if good else 1


def _universe_syms(args):
    up = os.path.join(OUT_DIR, "universe.txt")
    if args.symbols:
        return [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    if args.watchlist:
        if args.watchlist.endswith(".json"):
            d = json.load(open(args.watchlist, encoding="utf-8"))
            return [h["symbol"] for h in d.get("hits", [])]
        return _load_universe(args.watchlist)
    if os.path.exists(up):
        return _load_universe(up)
    return _load_universe(os.path.join(HERE, "bist100.txt"))


def cmd_daily(args):
    syms = _universe_syms(args)
    if args.limit:
        syms = syms[:args.limit]
    hits, scanned, failed = [], 0, 0
    print(f"{len(syms)} sembol için günlük kapanışlar...", file=sys.stderr)
    for s in syms:
        bars = B.candles(s, "3mo", "1d")
        if len(bars) < 21:
            failed += 1
            time.sleep(args.pause)
            continue
        if args.min_price and bars[-1]["c"] < args.min_price:
            time.sleep(args.pause)
            continue
        if args.min_volume and (bars[-1]["v"] or 0) < args.min_volume:
            time.sleep(args.pause)
            continue
        scanned += 1
        setups = analyze_daily(s, bars)
        if setups:
            hits.append({"symbol": s, "price": round(bars[-1]["c"], 2),
                         "setups": setups,
                         "pct_day": round((bars[-1]["c"] - bars[-2]["c"]) / bars[-2]["c"] * 100, 2)})
        time.sleep(args.pause)
    hits.sort(key=lambda h: (-len(h["setups"]), -h["pct_day"]))
    wl = {"mode": "daily", "as_of": B.now_ist().isoformat(timespec="minutes"),
          "market": B.market_state(), "scanned": scanned, "failed": failed,
          "hits": hits}
    if not args.no_write:
        _write(wl, os.path.join(OUT_DIR, "watchlist.json"))
    _print_hits(wl, args)
    return 0 if hits else 1


def _opening_range(bars5, when, or_minutes):
    """Bugünün ilk or_minutes dakikasının yüksek/düşüğü (İstanbul)."""
    o = when.replace(hour=B.OPEN_H, minute=B.OPEN_M, second=0, microsecond=0)
    end = o + dt.timedelta(minutes=or_minutes)
    rng_bars = []
    for b in bars5:
        t = dt.datetime.fromtimestamp(b["t"], B.IST)
        if t.date() == when.date() and o <= t < end:
            rng_bars.append(b)
    if not rng_bars:
        return None
    return {"high": max(b["h"] for b in rng_bars),
            "low": min(b["l"] for b in rng_bars),
            "end": end}


def cmd_orb(args):
    when = B.now_ist()
    if args.now:
        when = dt.datetime.fromisoformat(args.now).replace(tzinfo=B.IST)
    state = B.market_state(when)
    syms = _universe_syms(args)
    if args.limit:
        syms = syms[:args.limit]
    hits, scanned, failed = [], 0, 0
    print(f"ORB taraması, {when:%Y-%m-%d %H:%M} (İstanbul) — durum: {state}; "
          f"ilk {args.or_minutes} dk aralığı, 5dk bar.", file=sys.stderr)
    for s in syms:
        bars = B.candles(s, "1d", "5m")
        if not bars:
            failed += 1
            time.sleep(args.pause)
            continue
        rng = _opening_range(bars, when, args.or_minutes)
        if not rng:
            time.sleep(args.pause)
            continue
        scanned += 1
        after = [b for b in bars
                 if dt.datetime.fromtimestamp(b["t"], B.IST) >= rng["end"]
                 and dt.datetime.fromtimestamp(b["t"], B.IST) <= when]
        trig = next((b for b in after if b["c"] > rng["high"]), None)
        if trig:
            t = dt.datetime.fromtimestamp(trig["t"], B.IST)
            hits.append({"symbol": s, "price": round(trig["c"], 2),
                         "range_low": round(rng["low"], 2),
                         "range_high": round(rng["high"], 2),
                         "pct_over": round((trig["c"] - rng["high"]) / rng["high"] * 100, 2),
                         "time": t.strftime("%H:%M")})
        time.sleep(args.pause)
    hits.sort(key=lambda h: -h["pct_over"])
    wl = {"mode": "orb", "as_of": when.isoformat(timespec="minutes"),
          "market": state, "or_minutes": args.or_minutes,
          "scanned": scanned, "failed": failed, "hits": hits}
    if not args.no_write:
        _write(wl, os.path.join(OUT_DIR, "watchlist.json"))
    if state in ("kapali-hafta", "kapali-tatil", "acilis-oncesi"):
        print(f"UYARI: Borsa şu an {state}. ORB canlı değil; sonuç son işlem "
              f"gününe ait olabilir.", file=sys.stderr)
    _print_hits(wl, args)
    return 0 if hits else 1


def _print_hits(wl, args):
    if args.json:
        print(json.dumps(wl, ensure_ascii=False, indent=2))
        return
    hits = wl["hits"]
    show = hits[:args.show] if args.show else hits
    if wl["mode"] == "orb":
        print(f"\n{len(hits)} hisse açılış aralığını yukarı kırdı "
              f"({wl['scanned']} tarandı):")
        for h in show:
            print(f"  {h['time']}  {h['symbol']:<7} {h['price']:>9.2f} TL  "
                  f"aralık {h['range_low']}–{h['range_high']}  +{h['pct_over']}%")
    else:
        print(f"\n{len(hits)} hissede kurulum var ({wl['scanned']} tarandı):")
        for h in show:
            print(f"  {h['symbol']:<7} {h['price']:>9.2f} TL  "
                  f"gün {h['pct_day']:+.2f}%  [{', '.join(h['setups'])}]")
    if not hits:
        print("  (kurulum yok)")
    print("\nBir tarama alınacak hisse listesi değildir. Sıradaki: bir grafik "
          "seç, sonra bist-news ve bist-entry.")


def main():
    p = argparse.ArgumentParser(description="bist-scanner")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("universe", "daily", "orb"):
        sp = sub.add_parser(name)
        sp.add_argument("--pause", type=float, default=0.25)
        if name == "universe":
            sp.add_argument("--source")
        else:
            sp.add_argument("--symbols")
            sp.add_argument("--watchlist")
            sp.add_argument("--limit", type=int)
            sp.add_argument("--min-price", type=float, default=0)
            sp.add_argument("--min-volume", type=float, default=0)
            sp.add_argument("--show", type=int, default=0)
            sp.add_argument("--no-write", action="store_true")
            sp.add_argument("--json", action="store_true")
        if name == "orb":
            sp.add_argument("--or-minutes", type=int, default=15)
            sp.add_argument("--now")
    args = p.parse_args()
    return {"universe": cmd_universe, "daily": cmd_daily,
            "orb": cmd_orb}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
