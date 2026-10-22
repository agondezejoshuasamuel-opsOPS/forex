import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import DEMO_MODE, SYMBOL
from .curve_engine import analyze
from .indicators import calculate_indicators, finite
from .market import MarketEngine

market = MarketEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(market.run())
    yield
    market.running = False
    task.cancel()


app = FastAPI(title="Forex Curve Analyzer V1", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def index():
    return FileResponse("app/static/index.html")


def payload():
    df = market.dataframe()
    if len(df) >= 2:
        df = calculate_indicators(df)
    else:
        for col in ["ema20", "ema50", "rsi14", "macd", "macd_signal", "macd_hist", "atr14"]:
            df[col] = None

    analysis = analyze(df)

    candles = []
    for _, row in df.tail(160).iterrows():
        candles.append({
            "time": row["time"].isoformat(),
            "open": finite(row["open"]),
            "high": finite(row["high"]),
            "low": finite(row["low"]),
            "close": finite(row["close"]),
            "ema20": finite(row["ema20"]),
            "ema50": finite(row["ema50"]),
        })

    latest = df.iloc[-1] if len(df) else None

    return {
        "symbol": SYMBOL,
        "mode": "DEMO / SIMULATED" if DEMO_MODE else "LIVE",
        "price": finite(latest["close"]) if latest is not None else None,
        "ema20": finite(latest["ema20"]) if latest is not None else None,
        "ema50": finite(latest["ema50"]) if latest is not None else None,
        "rsi14": finite(latest["rsi14"]) if latest is not None else None,
        "macd": finite(latest["macd"]) if latest is not None else None,
        "macd_signal": finite(latest["macd_signal"]) if latest is not None else None,
        "atr14": finite(latest["atr14"]) if latest is not None else None,
        "analysis": analysis,
        "candles": candles,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await websocket.send_text(json.dumps(payload()))
            await asyncio.sleep(1)
    except Exception:
        pass
