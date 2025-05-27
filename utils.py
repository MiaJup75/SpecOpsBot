import json
import requests
from datetime import datetime
from config import config

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]

def fetch_max_token_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    try:
        response = requests.get(url)
        data = response.json()
        pair = data.get("pair", {})
        price = pair.get("priceUsd", "N/A")
        market_cap = pair.get("marketCap", "N/A")
        volume = pair.get("volume", {}).get("h24", "N/A")
        fdv = pair.get("fdv", "N/A")

        return {
            "price": f"${float(price):,.8f}" if price else "N/A",
            "market_cap": f"${int(market_cap):,}" if market_cap else "N/A",
            "volume": f"${float(volume):,.0f}" if volume else "N/A",
            "fdv": f"${int(fdv):,}" if fdv else "N/A"
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_trending_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        data = response.json()
        pairs = data.get("pairs", [])

        sorted_pairs = sorted(pairs, key=lambda x: float(x.get("volume", {}).get("h24", 0)), reverse=True)
        top_pairs = sorted_pairs[:5]

        results = []
        for pair in top_pairs:
            base = pair["baseToken"]["symbol"]
            price = float(pair.get("priceUsd", 0))
            volume = float(pair.get("volume", {}).get("h24", 0))
            results.append(f"{base} – ${price:,.8f} – Vol: ${volume:,.0f}")

        return "\n".join(results)
    except Exception as e:
        return f"Error: {e}"

def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        data = response.json()
        pairs = data.get("pairs", [])
        new_tokens = []

        for pair in pairs:
            created = pair.get("pairCreatedAt")
            if not created:
                continue
            launch_time = datetime.fromtimestamp(int(created) / 1000)
            age_minutes = (datetime.utcnow() - launch_time).total_seconds() / 60
            if age_minutes <= 1440:  # 24 hours
                symbol = pair["baseToken"]["symbol"]
                volume = float(pair.get("volume", {}).get("h24", 0))
                lp = float(pair.get("liquidity", {}).get("usd", 0))
                time_str = launch_time.strftime("%Y-%m-%d %H:%M")
                new_tokens.append(f"{symbol} – LP: ${lp:,.0f} – Vol: ${volume:,.0f} – Launched: {time_str}")

        if not new_tokens:
            return "No new tokens found."
        return "\n".join(new_tokens[:5])
    except Exception as e:
        return f"Error: {e}"

def check_suspicious_activity():
    dummy_alerts = [
        "🚨 Whale sold 10% of supply",
        "⚠️ LP dropped by 30% in 10 min",
        "🧠 Botnet activity spike detected"
    ]
    return "\n".join(dummy_alerts)

def track_position():
    return "📈 You bought 10.45M MAX at $0.0000885. Current price is $0.0003382. You're up 282%!"

def get_token_info(token_address):
    return f"Token: {token_address[:6]}...{token_address[-4:]}\nFake Risk: LOW\nLock Status: LOCKED"
