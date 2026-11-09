#!/usr/bin/env python3
"""kripto-oneri — Kripto Çok-Zaman-Dilimli Öneri (7/24).

Aynı teknik motor (indicators + recommend), veri Yahoo'dan (BTC-USD, ETH-USD...).
Gün içi + haftalık + aylık + yıllık adaylar, teknik + haber gerekçesiyle.
Kripto 7/24 işlem görür; borsa saati yoktur. Alım-satımı KULLANICI yapar.
Kripto çok oynaktır; kaldıraç/vadeli ÖNERİLMEZ.
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_bistlib"))
import screener as S  # noqa: E402

# Likit, Yahoo'da bulunan kripto evreni (-USD)
UNIVERSE = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD",
            "AVAX-USD", "DOGE-USD", "DOT-USD", "LINK-USD", "MATIC-USD", "TRX-USD",
            "LTC-USD", "ATOM-USD", "UNI-USD", "ETC-USD", "XLM-USD", "NEAR-USD",
            "APT-USD", "ARB-USD", "OP-USD", "INJ-USD", "FIL-USD", "RNDR-USD",
            "SUI-USD", "TON-USD", "SHIB-USD", "PEPE-USD", "AAVE-USD", "ICP-USD"]

CATALYST = ("etf", "listing", "listelen", "upgrade", "hard fork", "halving",
            "partnership", "ortaklık", "hack", "exploit", "regülasyon",
            "regulation", "sec", "yasak", "onay", "approval", "mainnet",
            "burn", "staking", "whale", "balina", "rekor", "all-time")


def news_query(sym):
    base = sym.replace("-USD", "")
    names = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "XRP": "XRP Ripple",
             "ADA": "Cardano", "DOGE": "Dogecoin", "BNB": "Binance Coin"}
    return f'{names.get(base, base)} kripto'


def main():
    p = argparse.ArgumentParser(description="kripto-oneri")
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
                      want_news=args.news, min_score=args.min_score, top=args.top,
                      buckets=buckets, pause=args.pause)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    S.render(result, title="KRİPTO ÖNERİLERİ (7/24, USD)", currency="USD",
             hours_note="Kripto 7/24 işlem görür; borsa saati yok. Oynaklık yüksek.",
             buckets=buckets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
