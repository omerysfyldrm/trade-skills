#!/usr/bin/env python3
"""bist-entry — Giriş Zamanlayıcı (long).

Bir hisseyi 5 dakikalık barlarla izler, açılış aralığını (İstanbul 10:00'dan
itibaren ilk 15 dk) kurar ve aralığın yüksekini (ya da verilen bir seviyeyi)
KAPANIŞLA aşan ilk tamamlanmış barda girişi işaret eder. Durumlar: beklemede,
tetiklendi, süresi-doldu, acilmadi. trader/entry.json yazar (bist-exit okur).
Emir YERLEŞTİRMEZ.
"""
import argparse, json, os, sys, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="bist-entry")
    p.add_argument("symbol", nargs="?", help="örn THYAO; yoksa watchlist'in ilki")
    p.add_argument("--level", type=float, help="aralık yerine bu seviyeyi kır")
    p.add_argument("--or-minutes", type=int, default=15)
    p.add_argument("--now", help="İstanbul saatini sabitle 'YYYY-MM-DD HH:MM'")
    p.add_argument("--min-vol-mult", type=float, default=0, help="tetik barı hacmi ort x katı")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    sym = args.symbol
    if not sym:
        wl = os.path.join("trader", "watchlist.json")
        if os.path.exists(wl):
            hits = json.load(open(wl, encoding="utf-8")).get("hits", [])
            sym = hits[0]["symbol"] if hits else None
    if not sym:
        print("Hisse ver: bist-entry THYAO", file=sys.stderr)
        return 1
    sym = sym.upper()

    when = dt.datetime.fromisoformat(args.now).replace(tzinfo=B.IST) if args.now else B.now_ist()
    state = B.market_state(when)
    bars = B.candles(sym, "1d", "5m")
    if not bars:
        print(f"{sym}: 5 dakikalık veri yok.", file=sys.stderr)
        return 1

    o = when.replace(hour=B.OPEN_H, minute=B.OPEN_M, second=0, microsecond=0)
    end = o + dt.timedelta(minutes=args.or_minutes)
    today = [b for b in bars if dt.datetime.fromtimestamp(b["t"], B.IST).date() == when.date()]
    rng_bars = [b for b in today if o <= dt.datetime.fromtimestamp(b["t"], B.IST) < end]

    result = {"symbol": sym, "as_of": when.isoformat(timespec="minutes"),
              "market": state, "or_minutes": args.or_minutes}

    if state in ("acilis-oncesi", "kapali-hafta", "kapali-tatil") and not args.now:
        result["status"] = "acilmadi"
        result["note"] = f"Borsa {state}."
    elif not rng_bars:
        result["status"] = "acilmadi"
        result["note"] = "Açılış aralığı henüz oluşmadı."
    else:
        rhigh = max(b["h"] for b in rng_bars)
        rlow = min(b["l"] for b in rng_bars)
        level = args.level if args.level else rhigh
        result.update({"range_low": round(rlow, 2), "range_high": round(rhigh, 2),
                       "level": round(level, 2)})
        after = [b for b in today
                 if dt.datetime.fromtimestamp(b["t"], B.IST) >= end
                 and dt.datetime.fromtimestamp(b["t"], B.IST) <= when]
        avgvol = (sum(b["v"] for b in today) / len(today)) if today else 0
        trig = None
        for b in after:
            if b["c"] > level:
                if args.min_vol_mult and avgvol and b["v"] < args.min_vol_mult * avgvol:
                    continue
                trig = b
                break
        last_c = today[-1]["c"] if today else None
        if trig:
            t = dt.datetime.fromtimestamp(trig["t"], B.IST)
            result.update({"status": "tetiklendi", "entry": round(trig["c"], 2),
                           "time": t.strftime("%H:%M"),
                           "pct_over": round((trig["c"] - level) / level * 100, 2)})
        elif when.time() > dt.time(13, 0):
            result.update({"status": "suresi-doldu", "last": round(last_c, 2) if last_c else None,
                           "note": "Öğleden sonra; yeni ORB girişi için geç."})
        else:
            dist = (level - last_c) / last_c * 100 if last_c else None
            result.update({"status": "beklemede", "last": round(last_c, 2) if last_c else None,
                           "to_trigger_pct": round(dist, 2) if dist is not None else None})

    os.makedirs("trader", exist_ok=True)
    json.dump(result, open(os.path.join("trader", "entry.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0

    print(f"{sym} — {result.get('status','?').upper()}  ({when:%H:%M} İstanbul)")
    if "range_high" in result:
        print(f"  açılış aralığı: {result['range_low']} – {result['range_high']}  (seviye {result['level']})")
    if result.get("status") == "tetiklendi":
        print(f"  GİRİŞ: {result['time']} @ {result['entry']} TL  (+{result['pct_over']}% seviye üstü)")
        print("  Sıradaki: bist-exit (stop + hedef).")
    elif result.get("status") == "beklemede":
        print(f"  son {result['last']} TL, tetiğe {result['to_trigger_pct']}% kaldı.")
    else:
        print(f"  {result.get('note','')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
