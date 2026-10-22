from .indicators import finite


def analyze(df):
    if len(df) < 55:
        return {
            "state": "warming up",
            "score": 0,
            "message": f"Collecting candles: {len(df)}/55 needed before the full analysis is active.",
            "details": ["The application is building enough price history for the indicators."],
            "ready": False,
        }

    row = df.iloc[-1]
    previous = df.iloc[-2]

    price = finite(row["close"])
    ema20 = finite(row["ema20"])
    ema50 = finite(row["ema50"])
    rsi = finite(row["rsi14"])
    macd = finite(row["macd"])
    signal = finite(row["macd_signal"])
    atr = finite(row["atr14"])
    previous_ema20 = finite(previous["ema20"])

    score = 0
    reasons = []

    if price is not None and ema20 is not None:
        if price > ema20:
            score += 1
            reasons.append("price is above EMA20")
        elif price < ema20:
            score -= 1
            reasons.append("price is below EMA20")

    if ema20 is not None and ema50 is not None:
        if ema20 > ema50:
            score += 2
            reasons.append("EMA20 is above EMA50")
        elif ema20 < ema50:
            score -= 2
            reasons.append("EMA20 is below EMA50")

    if previous_ema20 is not None and ema20 is not None:
        if ema20 > previous_ema20:
            score += 1
            reasons.append("EMA20 is sloping upward")
        elif ema20 < previous_ema20:
            score -= 1
            reasons.append("EMA20 is sloping downward")

    if macd is not None and signal is not None:
        if macd > signal:
            score += 2
            reasons.append("MACD is above its signal line")
        elif macd < signal:
            score -= 2
            reasons.append("MACD is below its signal line")

    if rsi is not None:
        if rsi >= 55:
            score += 1
            reasons.append("RSI shows positive momentum")
        elif rsi <= 45:
            score -= 1
            reasons.append("RSI shows negative momentum")
        else:
            reasons.append("RSI is near the middle, so momentum is mixed")

    if score >= 5:
        state = "strong upward"
        headline = "The curve is currently leaning strongly upward."
    elif score >= 2:
        state = "upward"
        headline = "The curve is currently leaning upward."
    elif score <= -5:
        state = "strong downward"
        headline = "The curve is currently leaning strongly downward."
    elif score <= -2:
        state = "downward"
        headline = "The curve is currently leaning downward."
    else:
        state = "sideways / uncertain"
        headline = "The curve is mixed, so there is no strong directional reading."

    details = []
    if rsi is not None:
        if rsi >= 70:
            details.append("RSI is above 70: recent upward momentum is strong, but the market may also be stretched.")
        elif rsi <= 30:
            details.append("RSI is below 30: recent downward momentum is strong, but the market may also be stretched.")
        else:
            details.append(f"RSI is {rsi:.1f}: momentum is not at an extreme level.")

    if atr is not None and price:
        atr_pct = (atr / price) * 100
        if atr_pct > 0.15:
            details.append("ATR indicates relatively high short-term movement for this price.")
        else:
            details.append("ATR indicates relatively modest short-term movement for this price.")

    details.append("This is a descriptive indicator-based reading, not a guarantee of the next price movement.")

    return {
        "state": state,
        "score": score,
        "message": headline,
        "details": details,
        "reasons": reasons,
        "ready": True,
    }
