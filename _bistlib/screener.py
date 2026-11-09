"""screener — piyasadan bağımsız çok-zaman-dilimli tarama + çıktı.

bist-oneri, kripto-oneri ve us-oneri bunu paylaşır. Yalnızca sembol listesi,
veri modu (raw) ve haber/katalizör kaynağı değişir; gösterge + kova mantığı
_bistlib/indicators + recommend'tan gelir.
"""
from __future__ import annotations
import time, sys
import bistlib as B
import recommend as R


def screen(symbols, *, raw, catalyst_kw, news_query=None, want_news=True,
           news_lang="tr", min_score=60, top=5,
           buckets=("gun_ici", "haftalik", "aylik", "yillik"),
           pause=0.25, rng="2y"):
    """Dönen: {bucket: [ {symbol, score, price, rsi, trend, reasons, temel} ]}."""
    scored = {b: [] for b in ("gun_ici", "haftalik", "aylik", "yillik")}
    print(f"{len(symbols)} sembol taranıyor...", file=sys.stderr)
    for s in symbols:
        daily = B.candles(s, rng, "1d", raw=raw)
        if len(daily) < 60:
            time.sleep(pause); continue
        res = R.classify(daily, B.resample(daily, "W"), B.resample(daily, "M"))
        if not res:
            time.sleep(pause); continue
        ind = res["_ind"]["daily"]
        for b in scored:
            if res[b]["score"] >= min_score:
                scored[b].append({"symbol": s, "score": res[b]["score"],
                                  "price": round(ind["last"], 4) if ind["last"] else None,
                                  "rsi": round(ind["rsi14"]) if ind["rsi14"] else None,
                                  "trend": ind["trend"], "reasons": res[b]["reasons"]})
        time.sleep(pause)

    out = {}
    for b in buckets:
        picks = sorted(scored[b], key=lambda x: -x["score"])[:top]
        if want_news:
            for rec in picks:
                q = news_query(rec["symbol"]) if news_query else rec["symbol"]
                items = B.google_news(q, limit=10, lang=news_lang)
                hits = []
                for it in items:
                    if any(k in it["title"].lower() for k in catalyst_kw):
                        hits.append(it["title"])
                    if len(hits) >= 2:
                        break
                rec["temel"] = hits
                time.sleep(pause)
        out[b] = picks
    return out


def render(result, *, title, currency="", hours_note="", buckets=None):
    buckets = buckets or ("gun_ici", "haftalik", "aylik", "yillik")
    print(f"\n═══ {title} ═══")
    if hours_note:
        print(hours_note)
    print("Tarama/sıralama, alım listesi değil. Alım-satım sana ait.\n")
    for b in buckets:
        picks = result.get(b, [])
        print(f"▌ {R.BUCKET_TR[b].upper()} tutuş  ({len(picks)} aday)")
        if not picks:
            print("   (ölçüte uyan yok)\n"); continue
        for rec in picks:
            cur = f" {currency}" if currency else ""
            print(f"  ● {rec['symbol']}  {rec['price']}{cur}  "
                  f"[skor {rec['score']}/100, RSI {rec['rsi']}, {rec['trend']}]")
            for r in rec["reasons"]:
                print(f"      • teknik: {r}")
            for t in rec.get("temel", []):
                print(f"      • temel : {t[:88]}")
        print()
    print("Not: teknik = grafik/ortalama/momentum; temel = haber başlıkları. "
          "Gerekçeleri oku, körlemesine alma.")
