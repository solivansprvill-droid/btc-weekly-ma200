#!/usr/bin/env python3
"""Fetch HYPE/USDC spot (pair index @107) daily candles from Hyperliquid's public API and build weekly candles.

Weekly candles start Monday 00:00 UTC (same as the BTC page).
Also stores the 200-day SMA as of each week's last trading day.
Output: data/hype_weekly.json. Python standard library only.
"""
import json
import os
import time
import urllib.request
from datetime import datetime, timezone, timedelta

API = "https://api.hyperliquid.xyz/info"
START_MS = 1732752000000  # 2024-11-28 UTC, before HYPE spot launch (2024-11-29)
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "hype_weekly.json")


def fetch_daily():
    body = json.dumps({"type": "candleSnapshot", "req": {
        "coin": "@107", "interval": "1d", "startTime": START_MS, "endTime": int(time.time() * 1000)}}).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json", "User-Agent": "hype-ma200-site"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                rows = json.load(r)
            break
        except Exception:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    return [(int(k["t"]) // 1000, float(k["o"]), float(k["h"]), float(k["l"]), float(k["c"]), float(k["v"])) for k in rows]


def to_weekly(days):
    weeks, closes = {}, []
    for ts, o, h, l, c, v in sorted(days):
        closes.append(c)
        ma200d = sum(closes[-200:]) / 200 if len(closes) >= 200 else None
        d = datetime.fromtimestamp(ts, timezone.utc)
        key = int((d - timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        w = weeks.get(key)
        if w is None:
            weeks[key] = [key, o, h, l, c, v, ma200d]
        else:
            w[2], w[3], w[4], w[5], w[6] = max(w[2], h), min(w[3], l), c, w[5] + v, ma200d
    r = lambda x: None if x is None else round(x, 4)
    return [[t, r(o), r(h), r(l), r(c), round(v, 2), r(m)] for t, o, h, l, c, v, m in sorted(weeks.values())]


def main():
    weekly = to_weekly(fetch_daily())
    payload = {
        "source": "Hyperliquid HYPE/USDC 现货",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fields": ["time", "open", "high", "low", "close", "volume", "ma200d"],
        "candles": weekly,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"wrote {len(weekly)} weekly candles, last close {weekly[-1][4]}")


if __name__ == "__main__":
    main()
