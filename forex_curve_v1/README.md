# Forex Curve Analyzer — Version 1

A beginner-friendly real-time EUR/USD forex curve dashboard.

## What Version 1 does

- Connects to a forex data provider through a small Python backend.
- Displays an updating EUR/USD price curve.
- Builds 1-minute OHLC candles from incoming prices.
- Calculates EMA 20, EMA 50, RSI 14, MACD and ATR 14.
- Produces a transparent trend score.
- Shows plain-English explanations of what the current curve and indicators mean.
- Includes a DEMO mode so the dashboard can run without an API key.

## Important

This is an analysis/education application, not a trading bot. It does not place trades and its messages are not financial advice. Indicator signals are descriptive and can be wrong.

## Requirements

- Python 3.10+
- Internet connection for live mode
- A market-data API key for live mode

## Install

```bash
cd forex_curve_v1
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
```

## Configure live data

Copy `.env.example` to `.env`.

Set:

```env
FOREX_API_KEY=YOUR_API_KEY
FOREX_PROVIDER=twelvedata
```

The application uses Twelve Data's WebSocket feed when a key is supplied.

Then run:

```bash
python run.py
```

Open:

http://127.0.0.1:8000

## Demo mode

If no API key is configured, the app automatically runs a clearly labelled simulated EUR/USD stream. This is useful for testing the interface and algorithm, but it is NOT real market data.

## Project structure

```text
forex_curve_v1/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── indicators.py
│   ├── curve_engine.py
│   ├── market.py
│   ├── main.py
│   ├── static/
│   │   ├── index.html
│   │   ├── app.js
│   │   └── style.css
│   └── templates/
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Algorithm

The trend score combines:

- Price above/below EMA20
- EMA20 above/below EMA50
- EMA20 slope
- MACD vs signal
- RSI region

The score is converted into:
- Strong upward
- Upward
- Sideways / uncertain
- Downward
- Strong downward

The explanatory messages also consider volatility using ATR.

Thresholds are intentionally simple in Version 1. They should be backtested before being used for any trading decision.
