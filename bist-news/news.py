#!/usr/bin/env python3
"""bist-news — BIST haber takipçisi.

İzlenen her hisse için Google News RSS (Türkçe, TR) başlıklarını çeker; bu
besleme KAP bildirimlerini de ("KAP *** XXX ***") başlık olarak getirir.
Sadece son kontrolden bu yana YENİ olanı gösterir, en yenisi üstte, günün
yüzde değişimiyle. Tekrarları ayıklar.

Veri: Google News RSS + Yahoo .IS fiyat. Botlara açık meşru beslemeler.
"""
import argparse, json, os, sys, time, datetime as dt, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402

STATE = os.path.join("trader", "news_seen.json")


def _watch_symbols(args):
    if args.symbols:
        return [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    wl = os.path.join("trader", "watchlist.json")
    if os.path.exists(wl):
        d = json.load(open(wl, encoding="utf-8"))
        return [h["symbol"] for h in d.get("hits", [])]
    return []


def _load_seen():
    if os.path.exists(STATE):
        try:
            return set(json.load(open(STATE, encoding="utf-8")))
        except Exception:                            # noqa: BLE001
            return set()
    return set()


def _save_seen(seen):
    os.makedirs("trader", exist_ok=True)
    json.dump(sorted(seen), open(STATE, "w", encoding="utf-8"))


def _tag(title):
    t = title.lower()
    tags = []
    for kw, tag in [("kap", "KAP"), ("bilanço", "bilanço"), ("kâr", "bilanço"),
                    ("temettü", "temettü"), ("hedef fiyat", "analist"),
                    ("tavsiye", "analist"), ("sermaye artır", "sermaye"),
                    ("bedelsiz", "bedelsiz"), ("halka arz", "halka-arz"),
                    ("ihale", "ihale"), ("sözleşme", "sözleşme"),
                    ("ceo", "yönetim"), ("istifa", "yönetim")]:
        if kw in t and tag not in tags:
            tags.append(tag)
    return tags


def main():
    p = argparse.ArgumentParser(description="bist-news")
    p.add_argument("--symbols", help="virgüllü; yoksa watchlist.json")
    p.add_argument("--limit", type=int, default=8, help="hisse başına haber")
    p.add_argument("--all", action="store_true", help="sadece yeni değil, hepsi")
    p.add_argument("--kap-only", action="store_true", help="sadece KAP bildirimleri")
    p.add_argument("--json", action="store_true")
    p.add_argument("--pause", type=float, default=0.4)
    args = p.parse_args()

    syms = _watch_symbols(args)
    if not syms:
        print("İzlenecek hisse yok. --symbols ver ya da önce bist-scanner çalıştır.",
              file=sys.stderr)
        return 1
    seen = set() if args.all else _load_seen()
    out, fresh = [], set()
    for s in syms:
        items = B.news_for_ticker(s, limit=args.limit, kap_only=args.kap_only)
        lp = B.last_price(s)
        new_items = []
        for it in items:
            h = hashlib.sha1(it["title"].encode()).hexdigest()[:12]
            fresh.add(h)
            if h in seen:
                continue
            new_items.append({**it, "tags": _tag(it["title"])})
        if new_items or args.all:
            out.append({"symbol": s,
                        "pct": round(lp["pct"], 2) if lp.get("pct") is not None else None,
                        "price": lp.get("price"),
                        "items": new_items})
        time.sleep(args.pause)

    if not args.all:
        _save_seen(seen | fresh)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    now = B.now_ist().strftime("%Y-%m-%d %H:%M")
    print(f"BIST haber taraması — {now} (İstanbul), durum: {B.market_state()}\n")
    total = 0
    for blk in out:
        if not blk["items"]:
            continue
        pct = blk["pct"]
        arrow = "" if pct is None else (f"  (gün {pct:+.2f}%)")
        print(f"● {blk['symbol']}{arrow}")
        for it in blk["items"]:
            total += 1
            tg = f" [{', '.join(it['tags'])}]" if it["tags"] else ""
            print(f"    - {it['title'][:95]}{tg}")
        print()
    if total == 0:
        print("Son kontrolden bu yana yeni haber yok. (Hepsini görmek için --all)")
    print("Not: Haber başlıkları Google News + KAP; işlem kararı için teyit et.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
