#!/usr/bin/env python3
"""us-oneri — ABD Borsası Çok-Zaman-Dilimli Öneri.

Aynı teknik motor (indicators + recommend), veri Yahoo'dan (AAPL, NVDA...).
Gün içi + haftalık + aylık + yıllık adaylar, teknik + haber gerekçesiyle
(İngilizce haber). Ham bilanço/temel için trader-analyst SEC EDGAR'dan okur.
Alım-satımı KULLANICI yapar; emir yerleştirilmez.
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_bistlib"))
import screener as S  # noqa: E402

# Likit ABD evreni (mega/large cap + popüler işlem isimleri)
UNIVERSE = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO",
            "AMD", "NFLX", "ADBE", "CRM", "COST", "PEP", "LLY", "JPM", "V",
            "MA", "UNH", "HD", "BAC", "XOM", "CVX", "WMT", "KO", "DIS", "INTC",
            "QCOM", "ORCL", "CSCO", "PLTR", "UBER", "COIN", "SHOP", "MU", "SMCI",
            "MRVL", "ARM", "SOFI", "HOOD", "DELL", "NOW", "PANW", "SNOW", "ABNB",
            "PYPL", "GS", "CAT", "BA", "GE"]

CATALYST = ("earnings", "guidance", "revenue", "beat", "miss", "upgrade",
            "downgrade", "price target", "acquisition", "merger", "deal",
            "partnership", "buyback", "dividend", "lawsuit", "contract",
            "product launch", "ai", "chip", "record", "layoff", "fda")


def news_query(sym):
    return f"{sym} stock"


def main():
    p = argparse.ArgumentParser(description="us-oneri")
    p.add_argument("--bucket", choices=["gun_ici", "haftalik", "aylik", "yillik", "all"],
                   default="all")
    p.add_argument("--symbols")
    p.add_argument("--min-score", type=int, default=60)
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--no-news", dest="news", action="store_false")
    p.add_argument("--pause", type=float, default=0.25)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    syms = ([s.strip().upper() for s in args.symbols.split(",")] if args.symbols
            else UNIVERSE)
    buckets = (("gun_ici", "haftalik", "aylik", "yillik") if args.bucket == "all"
               else (args.bucket,))
    result = S.screen(syms, raw=True, catalyst_kw=CATALYST, news_query=news_query,
                      want_news=args.news, news_lang="en", min_score=args.min_score,
                      top=args.top, buckets=buckets, pause=args.pause)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    S.render(result, title="ABD BORSASI ÖNERİLERİ (USD)", currency="USD",
             hours_note="ABD seansı 16:30–23:00 (İstanbul). Ham temel için trader-analyst (SEC).",
             buckets=buckets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
