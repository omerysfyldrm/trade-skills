#!/usr/bin/env python3
"""bist-oneri — BIST Çok-Zaman-Dilimli Hisse Önerisi.

'bist'i tara' dendiğinde: gün içi + haftalık + aylık + yıllık tutuş için
adaylar, HER biri teknik (grafik/ortalama/momentum) + temel (haber/KAP/anlaşma)
gerekçeyle. Tek günlük veri çeker, haftalık/aylık'ı türetir; göstergeleri
_bistlib/indicators + recommend ile hesaplar. Alım-satımı KULLANICI yapar.

Bu bir tarama/sıralamadır, kehanet değil. Çoğu işlemci para kaybeder.
"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_bistlib"))
import bistlib as B          # noqa: E402
import recommend as R        # noqa: E402

CATALYST = ("anlaşma", "ihale", "sözleşme", "yatırım", "bilanço", "kâr", "kar ",
            "temettü", "satın al", "ortaklık", "sermaye", "bedelsiz", "rekor",
            "ihracat", "teşvik", "fabrika", "kapasite", "hedef fiyat")


def load_universe():
    up = os.path.join("trader", "universe.txt")
    src = up if os.path.exists(up) else os.path.join(HERE, "..", "bist-scanner", "bist100.txt")
    return [l.split("|")[0].strip().upper() for l in open(src, encoding="utf-8")
            if l.strip() and not l.startswith("#")]


def news_reasons(sym):
    items = B.news_for_ticker(sym, limit=10)
    hits = []
    for it in items:
        t = it["title"].lower()
        if any(k in t for k in CATALYST):
            hits.append(it["title"])
        if len(hits) >= 2:
            break
    return hits


def main():
    p = argparse.ArgumentParser(description="bist-oneri")
    p.add_argument("--bucket", choices=["gun_ici", "haftalik", "aylik", "yillik", "all"],
                   default="all")
    p.add_argument("--symbols")
    p.add_argument("--limit", type=int, help="sadece ilk N sembolü tara")
    p.add_argument("--min-score", type=int, default=60)
    p.add_argument("--top", type=int, default=5, help="kova başına öneri")
    p.add_argument("--news", dest="news", default=True, action="store_true")
    p.add_argument("--no-news", dest="news", action="store_false")
    p.add_argument("--pause", type=float, default=0.25)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    syms = ([s.strip().upper() for s in args.symbols.split(",")] if args.symbols
            else load_universe())
    if args.limit:
        syms = syms[:args.limit]

    print(f"{len(syms)} hisse taranıyor (günlük+haftalık+aylık)...", file=sys.stderr)
    scored = {b: [] for b in ("gun_ici", "haftalik", "aylik", "yillik")}
    for s in syms:
        daily = B.candles(s, "2y", "1d")
        if len(daily) < 60:
            time.sleep(args.pause); continue
        weekly = B.resample(daily, "W")
        monthly = B.resample(daily, "M")
        res = R.classify(daily, weekly, monthly)
        if not res:
            time.sleep(args.pause); continue
        ind = res["_ind"]["daily"]
        for b in scored:
            sc = res[b]["score"]
            if sc >= args.min_score:
                scored[b].append({"symbol": s, "score": sc,
                                  "price": round(ind["last"], 2),
                                  "rsi": round(ind["rsi14"], 0) if ind["rsi14"] else None,
                                  "trend": ind["trend"],
                                  "reasons": res[b]["reasons"]})
        time.sleep(args.pause)

    buckets = list(scored) if args.bucket == "all" else [args.bucket]
    result = {}
    for b in buckets:
        top = sorted(scored[b], key=lambda x: -x["score"])[:args.top]
        if args.news:
            for rec in top:
                rec["temel"] = news_reasons(rec["symbol"])
                time.sleep(args.pause)
        result[b] = top

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0

    print(f"\n═══ BIST ÖNERİLERİ — {B.now_ist():%Y-%m-%d %H:%M} (borsa: {B.market_state()}) ═══")
    print("Tarama/sıralama, alım listesi değil. Alım-satım sana ait.\n")
    for b in buckets:
        top = result[b]
        print(f"▌ {R.BUCKET_TR[b].upper()} tutuş  ({len(top)} aday)")
        if not top:
            print("   (ölçüte uyan yok)\n"); continue
        for rec in top:
            print(f"  ● {rec['symbol']}  {rec['price']} TL  "
                  f"[skor {rec['score']}/100, RSI {rec['rsi']}, {rec['trend']}]")
            for r in rec["reasons"]:
                print(f"      • teknik: {r}")
            for t in rec.get("temel", []):
                print(f"      • temel : {t[:88]}")
        print()
    print("Not: Teknik = grafik/ortalama/momentum; temel = haber/KAP başlıkları "
          "(ham bilanço için bist-analyst --paste). Gerekçeleri oku, körlemesine alma.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
