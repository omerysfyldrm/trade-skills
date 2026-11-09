"""bistlib — BIST veri katmanı (ortak kütüphane).

Fiyat/grafik:  Yahoo Finance v8 chart ucu (.IS sembolleri, TRY).
Haber:         Google News RSS (ticker başına; KAP bildirimleri de başlık olarak gelir).
Takvim:        Borsa İstanbul saatleri (Europe/Istanbul): 10:00 açılış, 18:00 kapanış.

Hiçbir yerde tarayıcı kimliği taklit edilmez; yalnızca kendini tanıtan bir
istemci adı kullanılır. Kaynaklar botlara açık meşru genel beslemelerdir.
"""
from __future__ import annotations
import json, time, re, html, datetime as dt
import urllib.request, urllib.parse
from zoneinfo import ZoneInfo

IST = ZoneInfo("Europe/Istanbul")
UA = {"User-Agent": "bist-trader-skill/1.0 (+public data reader)"}

# --- Borsa İstanbul işlem takvimi -----------------------------------------
OPEN_H, OPEN_M = 10, 0        # sürekli işlem başlangıcı
CLOSE_H, CLOSE_M = 18, 0      # kapanış
# 2026-2027 resmi tatiller (BIST kapalı). Gerekirse güncelle.
HOLIDAYS_2026_2027 = {
    "2026-01-01", "2026-03-20", "2026-03-21", "2026-03-22", "2026-03-23",
    "2026-04-23", "2026-05-01", "2026-05-19", "2026-05-27", "2026-05-28",
    "2026-05-29", "2026-05-30", "2026-07-15", "2026-08-30", "2026-10-28",
    "2026-10-29",
    "2027-01-01", "2027-03-10", "2027-03-11", "2027-03-12", "2027-04-23",
    "2027-05-01", "2027-05-17", "2027-05-18", "2027-05-19", "2027-05-20",
    "2027-05-19", "2027-07-15", "2027-08-30", "2027-10-29",
}


def now_ist() -> dt.datetime:
    return dt.datetime.now(IST)


def is_trading_day(d: dt.date) -> bool:
    if d.weekday() >= 5:            # Cmt/Pzr
        return False
    return d.isoformat() not in HOLIDAYS_2026_2027


def market_state(when: dt.datetime | None = None) -> str:
    """'kapali-hafta', 'kapali-tatil', 'acilis-oncesi', 'acik', 'kapandi'."""
    when = when or now_ist()
    d = when.date()
    if when.weekday() >= 5:
        return "kapali-hafta"
    if not is_trading_day(d):
        return "kapali-tatil"
    o = when.replace(hour=OPEN_H, minute=OPEN_M, second=0, microsecond=0)
    c = when.replace(hour=CLOSE_H, minute=CLOSE_M, second=0, microsecond=0)
    if when < o:
        return "acilis-oncesi"
    if when > c:
        return "kapandi"
    return "acik"


# --- Sembol yardımcıları ---------------------------------------------------
def to_yahoo(symbol: str) -> str:
    """THYAO -> THYAO.IS. Zaten nokta içeriyorsa dokunma."""
    s = symbol.strip().upper()
    if not s:
        return s
    if "." in s:
        return s
    return s + ".IS"


def bare(symbol: str) -> str:
    return symbol.strip().upper().removesuffix(".IS")


# --- HTTP ------------------------------------------------------------------
def _get(url: str, headers: dict | None = None, timeout: int = 25,
         retries: int = 2) -> bytes:
    h = dict(UA)
    if headers:
        h.update(headers)
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:                       # noqa: BLE001
            last = e
            time.sleep(0.6 * (i + 1))
    raise last


# --- Yahoo chart -----------------------------------------------------------
def yahoo_chart(symbol: str, rng: str = "1mo", interval: str = "1d",
                raw: bool = False) -> dict:
    """Ham Yahoo chart sonucu (result[0]) ya da {} döner.

    raw=False: BIST, sembole .IS eklenir (TRY).
    raw=True : sembol olduğu gibi (ABD 'AAPL', kripto 'BTC-USD').
    """
    sym = symbol.strip().upper() if raw else to_yahoo(symbol)
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + urllib.parse.quote(sym)
           + f"?range={rng}&interval={interval}&includePrePost=false")
    try:
        d = json.loads(_get(url, {"Accept": "application/json"}))
    except Exception:                                # noqa: BLE001
        return {}
    res = (d.get("chart") or {}).get("result")
    if not res:
        return {}
    return res[0]


def candles(symbol: str, rng: str = "1mo", interval: str = "1d",
            raw: bool = False) -> list[dict]:
    """[{t,o,h,l,c,v}] zaman sırasıyla; boş/None barlar atılır."""
    r = yahoo_chart(symbol, rng, interval, raw=raw)
    if not r:
        return []
    ts = r.get("timestamp") or []
    q = (((r.get("indicators") or {}).get("quote") or [{}])[0]) or {}
    out = []
    for i, t in enumerate(ts):
        try:
            o = q["open"][i]; h = q["high"][i]; l = q["low"][i]
            c = q["close"][i]; v = (q.get("volume") or [None] * len(ts))[i]
        except (KeyError, IndexError, TypeError):
            continue
        if None in (o, h, l, c):
            continue
        out.append({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v or 0})
    return out


def resample(bars: list[dict], period: str) -> list[dict]:
    """Günlük barları haftalık ('W') ya da aylık ('M') OHLCV'ye indirger."""
    groups: dict = {}
    order: list = []
    for b in bars:
        d = dt.datetime.fromtimestamp(b["t"], IST).date()
        if period == "W":
            key = (d.isocalendar().year, d.isocalendar().week)
        elif period == "M":
            key = (d.year, d.month)
        else:
            key = d
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(b)
    out = []
    for key in order:
        g = groups[key]
        out.append({"t": g[0]["t"], "o": g[0]["o"],
                    "h": max(x["h"] for x in g), "l": min(x["l"] for x in g),
                    "c": g[-1]["c"], "v": sum(x["v"] for x in g)})
    return out


def last_price(symbol: str, raw: bool = False) -> dict:
    """{'price','currency','prev_close','pct'} ya da {}.

    Yüzde değişim bir ÖNCEKİ günün kapanışına göre hesaplanır.
    raw=True: sembolü olduğu gibi kullan (ABD/kripto).
    """
    r = yahoo_chart(symbol, "5d", "1d", raw=raw)
    if not r:
        return {}
    meta = r.get("meta") or {}
    px = meta.get("regularMarketPrice")
    # günlük kapanışlardan bir önceki günün kapanışını al
    q = (((r.get("indicators") or {}).get("quote") or [{}])[0]) or {}
    closes = [c for c in (q.get("close") or []) if c is not None]
    if px is None and closes:
        px = closes[-1]
    prev = None
    if closes:
        # px son bar ise ondan önceki, değilse son kapanış
        prev = closes[-2] if (len(closes) >= 2 and abs((px or 0) - closes[-1]) < 1e-9) else closes[-1]
    if prev is None:
        prev = meta.get("chartPreviousClose")
    pct = ((px - prev) / prev * 100) if (px and prev) else None
    return {"price": px, "currency": meta.get("currency"),
            "prev_close": prev, "pct": pct,
            "exchange": meta.get("exchangeName")}


# --- Google News RSS (KAP bildirimleri dahil) ------------------------------
def google_news(query: str, limit: int = 15, lang: str = "tr") -> list[dict]:
    """Ticker/konu için [{title,link,pub,source}].

    lang='tr' -> Türkçe/TR, lang='en' -> İngilizce/US.
    """
    q = urllib.parse.quote(query)
    if lang == "en":
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    else:
        url = f"https://news.google.com/rss/search?q={q}&hl=tr&gl=TR&ceid=TR:tr"
    try:
        xml = _get(url).decode("utf-8", "replace")
    except Exception:                                # noqa: BLE001
        return []
    items = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.S):
        def pick(tag):
            m = re.search(rf"<{tag}.*?>(.*?)</{tag}>", block, re.S)
            return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""
        title = pick("title")
        if not title:
            continue
        items.append({"title": title, "link": pick("link"),
                      "pub": pick("pubDate"), "source": pick("source")})
        if len(items) >= limit:
            break
    return items


def news_for_ticker(ticker: str, limit: int = 12, kap_only: bool = False) -> list[dict]:
    t = bare(ticker)
    q = f'"{t}" hisse OR KAP' if not kap_only else f'"{t}" KAP'
    items = google_news(q, limit=limit * 2)
    if kap_only:
        items = [i for i in items if "KAP" in i["title"].upper()]
    return items[:limit]
