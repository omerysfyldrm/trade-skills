#!/usr/bin/env python3
"""bist-derinlik — Emir Defteri (Kademe) Analizi.

Gerçek zamanlı derinlik (Level 2) ücretsiz API'de yoktur; Midas/Matriks'te
canlı görürsün. Oradaki kademe tablosunu kopyala, bir dosyaya yapıştır; bu
skill alış/satış hacim dengesizliğini, en büyük 'duvarları' (destek/direnç
olarak yığılan emirler), spread'i ve alım-satım baskısını çıkarır.

Beklenen yapıştırma biçimleri (toleranslı):
  a) 'ALIS_ADET  ALIS_FIYAT   SATIS_FIYAT  SATIS_ADET'  (kademe ladder, 5-10 satır)
  b) 'FIYAT ADET' çiftleri — bu durumda --split ile alış/satış ayır.

Kullanım: bist-derinlik --paste derinlik.txt [--symbol THYAO]
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import parsetr as P  # noqa: E402


def analyze(bids, asks):
    bid_vol = sum(q for _, q in bids)
    ask_vol = sum(q for _, q in asks)
    tot = bid_vol + ask_vol
    imb = (bid_vol - ask_vol) / tot * 100 if tot else 0
    best_bid = max((p for p, _ in bids), default=None)
    best_ask = min((p for p, _ in asks), default=None)
    spread = (best_ask - best_bid) if (best_bid and best_ask) else None
    spread_pct = (spread / best_bid * 100) if (spread and best_bid) else None
    bid_wall = max(bids, key=lambda x: x[1], default=None)
    ask_wall = max(asks, key=lambda x: x[1], default=None)
    return {"bid_vol": bid_vol, "ask_vol": ask_vol, "imbalance_pct": round(imb, 1),
            "best_bid": best_bid, "best_ask": best_ask,
            "spread": round(spread, 4) if spread is not None else None,
            "spread_pct": round(spread_pct, 3) if spread_pct is not None else None,
            "bid_wall": bid_wall, "ask_wall": ask_wall}


def main():
    p = argparse.ArgumentParser(description="bist-derinlik")
    p.add_argument("--paste", required=True)
    p.add_argument("--symbol", default="")
    p.add_argument("--split", type=float,
                   help="'FIYAT ADET' biçimi için: bu fiyatın altı alış, üstü satış")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if not os.path.exists(args.paste):
        print(f"Dosya yok: {args.paste}. Midas'taki kademe tablosunu .txt'ye yapıştır.",
              file=sys.stderr)
        return 1
    d = P.depth_rows(open(args.paste, encoding="utf-8").read())
    bids, asks = d["bids"], d["asks"]
    if not bids and not asks and d["generic"]:
        if args.split:
            for price, qty in d["generic"]:
                (bids if price <= args.split else asks).append((price, qty))
        else:
            print("Biçim 'FIYAT ADET' çiftleri gibi; alış/satışı ayırmak için "
                  "--split <orta_fiyat> ver (örn son fiyat).", file=sys.stderr)
            return 1
    if not bids and not asks:
        print("Kademe okunamadı. Beklenen: 'alış_adet alış_fiyat satış_fiyat satış_adet' "
              "ya da 'fiyat adet' + --split.", file=sys.stderr)
        return 1

    a = analyze(bids, asks)
    if a["imbalance_pct"] > 20:
        sig = "Alış baskısı ağır basıyor (alış hacmi > satış)."
    elif a["imbalance_pct"] < -20:
        sig = "Satış baskısı ağır basıyor (satış hacmi > alış)."
    else:
        sig = "Defter dengeli; net baskı zayıf."

    out = {"symbol": args.symbol.upper(), **a, "signal": sig,
           "bid_levels": len(bids), "ask_levels": len(asks)}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    print(f"Emir Defteri / Derinlik{(' — ' + out['symbol']) if out['symbol'] else ''}  "
          f"({len(bids)} alış / {len(asks)} satış kademesi)")
    print(f"  En iyi alış: {a['best_bid']}  | en iyi satış: {a['best_ask']}  "
          f"| spread: {a['spread']} ({a['spread_pct']}%)" if a['spread'] is not None else
          f"  En iyi alış: {a['best_bid']} | en iyi satış: {a['best_ask']}")
    print(f"  Toplam alış adedi: {a['bid_vol']:,.0f} | satış adedi: {a['ask_vol']:,.0f}")
    print(f"  Dengesizlik: {a['imbalance_pct']:+.1f}%  (+ alış lehine, - satış lehine)")
    if a["bid_wall"]:
        print(f"  En büyük alış duvarı (destek): {a['bid_wall'][1]:,.0f} adet @ {a['bid_wall'][0]}")
    if a["ask_wall"]:
        print(f"  En büyük satış duvarı (direnç): {a['ask_wall'][1]:,.0f} adet @ {a['ask_wall'][0]}")
    print(f"  Sinyal: {sig}")
    print("\n  Not: Derinlik anlıktır ve hızla değişir, sahte duvarlar (spoofing) "
          "olabilir; tek başına karar verme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
