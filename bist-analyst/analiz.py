#!/usr/bin/env python3
"""bist-analyst — Bilanço/Analist Takibi (BIST).

KAP'ın ham XBRL'i botlara kapalı olduğundan, bu skill meşru kaynaklardan
okunabilir olanı toplar: bir hisse için bilanço/temettü/hedef-fiyat haberleri
(Google News, KAP bildirimleri dahil), fiyatın 20 ve 50 günlük ortalamaya göre
duruşu ve son çeyreklik getiri. Daha derin okuma için KAP bilanço tablosunu
metin olarak --paste ile verebilirsin; o metni Claude özetler.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bistlib"))
import bistlib as B  # noqa: E402

FIN_KW = ("bilanço", "kâr", "kar ", "zarar", "temettü", "hedef fiyat",
          "tavsiye", "ciro", "gelir", "net dönem", "faaliyet", "çeyrek",
          "finansal", "sermaye", "bedelsiz")


def sma(vals, n):
    return sum(vals[-n:]) / n if len(vals) >= n else None


def main():
    p = argparse.ArgumentParser(description="bist-analyst")
    p.add_argument("symbol")
    p.add_argument("--paste", help="KAP bilanço metni dosyası (Claude özetler)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    sym = args.symbol.upper()

    if args.paste:
        txt = open(args.paste, encoding="utf-8").read()
        print(f"[{sym}] Yapıştırılan bilanço metni ({len(txt)} karakter) okundu. "
              f"Claude bunu özetleyecek:\n")
        print(txt[:4000])
        return 0

    bars = B.candles(sym, "6mo", "1d")
    closes = [b["c"] for b in bars]
    news = B.news_for_ticker(sym, limit=20)
    fin = [n for n in news if any(k in n["title"].lower() for k in FIN_KW)]

    ma20, ma50 = sma(closes, 20), sma(closes, 50)
    last = closes[-1] if closes else None
    q_ret = (last / closes[-63] - 1) * 100 if len(closes) >= 63 and closes[-63] else None

    trend = "?"
    if last and ma20 and ma50:
        if last > ma20 > ma50:
            trend = "yukarı (fiyat > 20g > 50g ortalama)"
        elif last < ma20 < ma50:
            trend = "aşağı (fiyat < 20g < 50g ortalama)"
        else:
            trend = "karışık"

    out = {"symbol": sym, "last": round(last, 2) if last else None,
           "ma20": round(ma20, 2) if ma20 else None,
           "ma50": round(ma50, 2) if ma50 else None,
           "trend": trend, "quarter_return_pct": round(q_ret, 1) if q_ret else None,
           "fin_news": fin[:8]}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    print(f"{sym} — Analist/Bilanço Özeti")
    print(f"  Fiyat {out['last']} | 20g ort {out['ma20']} | 50g ort {out['ma50']}")
    print(f"  Trend: {trend}")
    if q_ret is not None:
        print(f"  Son ~çeyrek getiri: {q_ret:+.1f}%")
    print("  Bilanço/analist haberleri:")
    if fin:
        for n in fin[:8]:
            print(f"    - {n['title'][:95]}")
    else:
        print("    (bu hisse için finansal haber başlığı bulunamadı)")
    print("\n  Derin bilanço okuması için KAP finansal tablosunu kopyala: "
          "bist-analyst " + sym + " --paste dosya.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
