#!/usr/bin/env python3
"""piyasa-duygu — Lider/Makro Haber & Duygu Analizi (haber tabanlı).

Piyasayı oynatan kişilerin ve kurumların haberlere YANSIYAN açıklamalarını ve
makro başlıkları çeker (Google News), basit bir sözlükle risk-açık/risk-kapalı
tonu etiketler ve kısa bir makro brifing verir. BIST + ABD + kripto ortak bağlam.

NOT: Belirli X/Twitter hesapları kazınmaz (API'siz yasak/engelli). Bu skill
liderlerin söylediklerinin HABERE yansımasını okur; duygu sözlük tabanlıdır,
derin NLP değil — yön değil bağlam verir.
"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_bistlib"))
import bistlib as B  # noqa: E402

# (etiket, sorgu, dil)
TOPICS = [
    ("Fed / Powell faiz", "Federal Reserve Powell interest rate", "en"),
    ("ABD enflasyon / CPI", "US inflation CPI", "en"),
    ("Trump / politika", "Trump tariffs policy market", "en"),
    ("ECB Avrupa", "ECB European Central Bank rate", "en"),
    ("TCMB / faiz", "TCMB faiz kararı", "tr"),
    ("Türkiye ekonomi / enflasyon", "Türkiye enflasyon ekonomi", "tr"),
    ("Jeopolitik / petrol", "geopolitics war oil price", "en"),
    ("Bitcoin / kripto regülasyon", "Bitcoin ETF crypto regulation SEC", "en"),
    ("Borsa İstanbul / BIST", "Borsa İstanbul BIST100 yabancı", "tr"),
]

POS = ("anlaşma", "indirim", "rekor", "büyüme", "onay", "teşvik", "rally",
       "cut", "deal", "beat", "record", "surge", "approval", "ease", "growth",
       "optimis", "yükseliş", "pozitif", "destek", "canlan")
NEG = ("savaş", "yaptırım", "enflasyon", "faiz artır", "kriz", "yasak", "çöküş",
       "war", "sanction", "hike", "crisis", "ban", "crash", "recession", "selloff",
       "fear", "düşüş", "zayıf", "risk", "tension", "gerginlik", "iflas", "resesyon")


def tone(title):
    t = title.lower()
    p = sum(k in t for k in POS)
    n = sum(k in t for k in NEG)
    if p > n:
        return "+"
    if n > p:
        return "-"
    return "0"


def main():
    p = argparse.ArgumentParser(description="piyasa-duygu")
    p.add_argument("--topics", help="virgüllü ek sorgu(lar)")
    p.add_argument("--per", type=int, default=4, help="konu başına başlık")
    p.add_argument("--pause", type=float, default=0.4)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    topics = list(TOPICS)
    if args.topics:
        for q in args.topics.split(","):
            topics.append((q.strip(), q.strip(), "tr"))

    blocks, score = [], 0
    for label, query, lang in topics:
        items = B.google_news(query, limit=args.per, lang=lang)
        toned = [{"title": it["title"], "tone": tone(it["title"])} for it in items]
        for it in toned:
            score += 1 if it["tone"] == "+" else (-1 if it["tone"] == "-" else 0)
        blocks.append({"label": label, "items": toned})
        time.sleep(args.pause)

    mood = ("RİSK-AÇIK (haber tonu pozitif)" if score >= 3 else
            "RİSK-KAPALI (haber tonu negatif)" if score <= -3 else
            "KARIŞIK / NÖTR")
    out = {"as_of": B.now_ist().strftime("%Y-%m-%d %H:%M"), "mood": mood,
           "score": score, "topics": blocks}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    print(f"═══ PİYASA DUYGU / MAKRO BRİFİNG — {out['as_of']} (İstanbul) ═══")
    print(f"Genel ton: {mood}  (net skor {score:+d})\n")
    for blk in blocks:
        tones = [i["tone"] for i in blk["items"]]
        tag = ("+" if tones.count("+") > tones.count("-") else
               "-" if tones.count("-") > tones.count("+") else "0")
        print(f"▌ {blk['label']}  [{tag}]")
        for it in blk["items"][:args.per]:
            print(f"    {it['tone']}  {it['title'][:92]}")
        print()
    print("Not: Sözlük tabanlı ton, derin analiz değil; yön değil BAĞLAM verir. "
          "Belirli sosyal medya hesapları okunmaz (API gerekir).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
