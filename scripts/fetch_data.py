#!/usr/bin/env python3
"""Fetch BTC/USD daily candles from Bitstamp (data begins 2011-08) and build weekly candles.

Weekly candles start Monday 00:00 UTC. Output: data/btc_weekly.json
Only uses the Python standard library.
"""
import json
import os
import time
import urllib.request
from datetime import datetime, timezone, timedelta

API = "https://www.bitstamp.net/api/v2/ohlc/btcusd/?step=86400&limit=1000&start={start}"
START = 1313020800  # 2011-08-11 UTC, before Bitstamp's first trade
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "btc_weekly.json")


def fetch_daily():
    days, start = {}, START
    now = int(time.time())
    while start < now:
        req = urllib.request.Request(API.format(start=start), headers={"User-Agent": "btc-ma200-site"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    rows = json.load(r)["data"]["ohlc"]
                break
            except Exception as e:  # network hiccup: back off and retry
                if attempt == 3:
                    raise
                time.sleep(5 * (attempt + 1))
        if not rows:
            break
        for k in rows:
            ts = int(k["timestamp"])
            days[ts] = (float(k["open"]), float(k["high"]), float(k["low"]), float(k["close"]), float(k["volume"]))
        last = int(rows[-1]["timestamp"])
        if last + 86400 <= start:
            break
        start = last + 86400
        time.sleep(0.4)
    return dict(sorted(days.items()))


def to_weekly(days):
    weeks = {}
    for ts, (o, h, l, c, v) in days.items():
        if v == 0 and o == h == l == c:
            continue  # skip empty no-trade days
        d = datetime.fromtimestamp(ts, timezone.utc)
        monday = (d - timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        key = int(monday.timestamp())
        w = weeks.get(key)
        if w is None:
            weeks[key] = [key, o, h, l, c, v]
        else:
            w[2] = max(w[2], h)
            w[3] = min(w[3], l)
            w[4] = c
            w[5] += v
    return [[t, round(o, 2), round(h, 2), round(l, 2), round(c, 2), round(v, 2)] for t, o, h, l, c, v in sorted(weeks.values())]


def main():
    weekly = to_weekly(fetch_daily())
    payload = {
        "source": "Bitstamp BTC/USD",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fields": ["time", "open", "high", "low", "close", "volume"],
        "candles": weekly,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"wrote {len(weekly)} weekly candles, last close {weekly[-1][4]}")


if __name__ == "__main__":
    main()
