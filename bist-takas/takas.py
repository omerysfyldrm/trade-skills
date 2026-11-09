#!/usr/bin/env python3
"""bist-takas — Aracı Kurum Dağılımı & Takas Analizi.

Bu veri (hangi aracı kurum net aldı/sattı, takas yoğunlaşması) İş Yatırım/
Matriks gibi bot-korumalı/ücretli kaynaklardadır; otomatik çekilmez. Sen
Midas/İş Yatırım'da bu tabloya erişiyorsun: kopyala, bir dosyaya yapıştır,
bu skill yapılandırıp sinyale çevirir — net alıcılar/satıcılar, net para
akışı, yoğunlaşma (ilk 3 kurumun payı) ve toplama/dağıtım işareti.

Kullanım: bist-takas --paste takas.txt  [--symbol THYAO]
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import parsetr as P  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="bist-takas")
    p.add_argument("--paste", required=True, help="yapıştırılan takas/aracı dağılım tablosu (dosya)")
    p.add_argument("--symbol", default="")
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if not os.path.exists(args.paste):
        print(f"Dosya yok: {args.paste}. Tabloyu kopyalayıp bir .txt'ye yapıştır.",
              file=sys.stderr)
        return 1
    text = open(args.paste, encoding="utf-8").read()
    rows = [r for r in P.broker_rows(text) if r.get("net") is not None]
    if not rows:
        print("Tabloda satır okunamadı. Beklenen: her satırda 'Kurum Alış Satış' "
              "ya da 'Kurum Net'. Claude ham metni de yorumlayabilir.", file=sys.stderr)
        return 1

    buyers = sorted([r for r in rows if r["net"] > 0], key=lambda r: -r["net"])
    sellers = sorted([r for r in rows if r["net"] < 0], key=lambda r: r["net"])
    total_buy = sum(r["net"] for r in buyers)
    total_sell = -sum(r["net"] for r in sellers)
    net_flow = total_buy - total_sell
    top3_share = (sum(r["net"] for r in buyers[:3]) / total_buy * 100) if total_buy else 0

    if net_flow > 0 and top3_share > 50:
        signal = "Toplama: az sayıda kurum net alıyor (yoğun, güçlü sinyal)."
    elif net_flow > 0:
        signal = "Hafif toplama: net alım var, dağınık."
    elif net_flow < 0 and total_sell and (-sum(r['net'] for r in sellers[:3]) / total_sell) > 0.5:
        signal = "Dağıtım: az sayıda kurum net satıyor (yoğun)."
    else:
        signal = "Belirsiz/dengeli: net akış zayıf."

    out = {"symbol": args.symbol.upper(), "rows": len(rows),
           "net_buyers": buyers[:args.top], "net_sellers": sellers[:args.top],
           "total_net_buy": round(total_buy, 2), "total_net_sell": round(total_sell, 2),
           "net_flow": round(net_flow, 2), "top3_buy_concentration_pct": round(top3_share, 1),
           "signal": signal}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    print(f"Takas / Aracı Kurum Dağılımı{(' — ' + out['symbol']) if out['symbol'] else ''}  "
          f"({len(rows)} kurum)")
    print(f"\n  En çok NET ALAN {min(args.top,len(buyers))}:")
    for r in buyers[:args.top]:
        print(f"    + {r['name'][:28]:<28} net {r['net']:>14,.0f}")
    print(f"  En çok NET SATAN {min(args.top,len(sellers))}:")
    for r in sellers[:args.top]:
        print(f"    - {r['name'][:28]:<28} net {r['net']:>14,.0f}")
    print(f"\n  Toplam net alım: {total_buy:,.0f} | net satım: {total_sell:,.0f}")
    print(f"  NET AKIŞ: {net_flow:+,.0f}   | ilk 3 alıcı yoğunlaşması: {top3_share:.1f}%")
    print(f"  Sinyal: {signal}")
    print("\n  Not: Takas tek başına yön vermez; fiyat/hacim ve haberle birlikte oku.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
