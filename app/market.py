import asyncio
import json
import math
import random
from datetime import datetime, timezone

import httpx
import pandas as pd
import websockets

from .config import API_KEY, DEMO_MODE, SYMBOL


class MarketEngine:
    def __init__(self):
        self.prices = []
        self.running = True
        self.last_price = 1.08250

    def seed_demo_history(self, count=160):
        price = self.last_price
        rows = []
        now = pd.Timestamp.now(tz="UTC").floor("min")

        for i in range(count, 0, -1):
            drift = random.gauss(0, 0.00012)
            price = max(0.5, price + drift)
            high = price + abs(random.gauss(0, 0.00006))
            low = price - abs(random.gauss(0, 0.00006))
            open_price = price + random.gauss(0, 0.00005)
            close = price

            rows.append({
                "time": now - pd.Timedelta(minutes=i),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
            })

        self.prices = rows

    async def demo_stream(self):
        if not self.prices:
            self.seed_demo_history()

        while self.running:
            await asyncio.sleep(1)
            # Simulated ticks for UI/algorithm testing only.
            self.last_price += random.gauss(0, 0.000025)
            self.last_price = max(0.5, self.last_price)
            self._add_tick(self.last_price)

    def _add_tick(self, price):
        now = pd.Timestamp.now(tz="UTC").floor("min")

        if not self.prices or self.prices[-1]["time"] != now:
            self.prices.append({
                "time": now,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
            })
        else:
            candle = self.prices[-1]
            candle["high"] = max(candle["high"], price)
            candle["low"] = min(candle["low"], price)
            candle["close"] = price

        self.prices = self.prices[-2000:]

    async def twelvedata_stream(self):
        url = "wss://ws.twelvedata.com/v1/quotes/price"

        async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
            await ws.send(json.dumps({
                "action": "subscribe",
                "params": {"symbols": SYMBOL},
                "apikey": API_KEY,
            }))

            async for raw in ws:
                data = json.loads(raw)

                if data.get("event") == "price":
                    price = data.get("price")
                    try:
                        price = float(price)
                    except (TypeError, ValueError):
                        continue

                    if math.isfinite(price):
                        self.last_price = price
                        self._add_tick(price)

    async def run(self):
        if DEMO_MODE:
            await self.demo_stream()
            return

        try:
            await self.twelvedata_stream()
        except Exception as exc:
            # Keep the application alive and fall back to a visible simulation.
            print(f"Live feed stopped: {exc}")
            print("Falling back to DEMO mode. Check your API key/provider configuration.")
            await self.demo_stream()

    def dataframe(self):
        if not self.prices:
            return pd.DataFrame(columns=["time", "open", "high", "low", "close"])

        return pd.DataFrame(self.prices)
