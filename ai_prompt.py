# ai_prompt.py – AI Trade Prompting Engine (Mock Logic)

def get_ai_trade_prompt(token_data: dict) -> str:
    """
    Mock logic for suggesting a trade prompt based on token stats.
    Replace this with a real ML model or heuristics later.
    """
    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    price = float(token_data.get("price", 0))
    mcap = float(token_data.get("market_cap", 0))
    volume = float(token_data.get("volume", 0))
    buys = int(token_data.get("buys", 0))
    sells = int(token_data.get("sells", 0))
    change = float(token_data.get("change", 0))

    if mcap < 250000 and volume > 100000 and buys > sells and change > 10:
        return f"🤖 AI Suggestion: Consider <b>BUYING</b> ${symbol.upper()} – early momentum forming."
    elif mcap > 750000 and sells > buys and change < -10:
        return f"⚠️ AI Suggestion: Consider <b>SELLING</b> ${symbol.upper()} – signs of distribution."
    elif volume < 10000:
        return f"🕵️ AI Suggestion: <b>AVOID</b> ${symbol.upper()} – low volume/liquidity."
    else:
        return f"📊 AI Suggestion: <b>HOLD/WAIT</b> on ${symbol.upper()} – no strong signal yet."
