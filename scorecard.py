# scorecard.py – Post-Launch Token Scorecard

def generate_scorecard(token_data):
    try:
        symbol = token_data.get("symbol", "N/A")
        price = float(token_data.get("price", 0))
        market_cap = int(float(token_data.get("market_cap", 0)))
        volume = int(float(token_data.get("volume", 0)))
        buys = token_data.get("txns", {}).get("buys", 0)
        sells = token_data.get("txns", {}).get("sells", 0)
        liquidity = float(token_data.get("liquidity", 0))
        launched = token_data.get("pair_created_at", "N/A")
        link = token_data.get("dexscreener_link", "#")

        score = 0
        if market_cap > 100000: score += 1
        if volume > 50000: score += 1
        if buys > sells: score += 1
        if liquidity > 20000: score += 1
        if "rug" not in token_data.get("risk", "").lower(): score += 1

        rating = ["❌", "⚠️", "🟡", "🟢", "✅", "🌟"][min(score, 5)]

        message = f"""
<b>📊 Post-Launch Scorecard for ${symbol}</b>

💰 Price: ${price:.6f}
🏷️ Market Cap: ${market_cap:,}
📈 Volume (24h): ${volume:,}
📥 Buys: {buys} | 📤 Sells: {sells}
💧 Liquidity: ${liquidity:,.0f}
🚀 Launched: {launched}

<b>Score: {score}/5 {rating}</b>
🔗 <a href="{link}">Dexscreener</a>
""".strip()

        return message
    except Exception as e:
        return f"⚠️ Error generating scorecard: {e}"
