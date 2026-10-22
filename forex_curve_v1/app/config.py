import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOREX_API_KEY", "").strip()
PROVIDER = os.getenv("FOREX_PROVIDER", "twelvedata").strip().lower()
SYMBOL = os.getenv("SYMBOL", "EUR/USD").strip()
DEMO_MODE = os.getenv("DEMO_MODE", "true").strip().lower() == "true" or not API_KEY
