import requests
from config import config

MAX_TOKEN_ADDRESS = config["max_token"]
TRACKED_WALLETS = config["wallets"]

def fetch_max_token_data():
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch data")
    
    data = response.json().get("pair", {})
    return {
        "price": float(data.get("priceUsd", 0)),
        "market_cap": float(data.get("marketCap", 0)),
        "volume": float(data.get("volume", {}).get("h24", 0)),
        "fdv": float(data.get("fdv", 0)),
        "buys": data.get("txns", {}).get("h24", {}).get("buys", 0),
        "sells": data.get("txns", {}).get("h24", {}).get("sells", 0),
        "liquidity": float(data.get("liquidity", {}).get("usd", 0)),
        "change": data.get("priceChange", {}).get("h24", 0),
        "holders": "N/A",  # Placeholder
        "launch_time": data.get("pairCreatedAt", "N/A"),
        "dex_url": f"https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    }

def fetch_trending_tokens():
    tokens = [
        {"name": "DOGGO", "price": 0.0009, "volume": 12345},
        {"name": "MEOW", "price": 0.0012, "volume": 8901},
        {"name": "ZAP", "price": 0.045, "volume": 22000},
        {"name": "RAWR", "price": 0.00005, "volume": 3210},
        {"name": "BLOOP", "price": 0.75, "volume": 18450},
    ]
    lines = [f"{i+1}. {t['name']} – ${t['price']} – Vol: ${t['volume']:,.0f}" for i, t in enumerate(tokens)]
    return "🚀 <b>Trending Solana Meme Coins</b>\n" + "\n".join(lines)

def fetch_new_tokens():
    new_tokens = []  # Stub list
    if not new_tokens:
        return "No new tokens found."
    return "\n".join(f"🆕 {t['name']}" for t in new_tokens)

def check_suspicious_activity():
    alerts = [
        {"token": "RUGDOG", "reason": "💥 Liquidity pulled"},
        {"token": "FAKEAI", "reason": "⚠️ Dev wallet dumped 80%"},
    ]
    if not alerts:
        return "No suspicious activity detected."
    return "⚠️ <b>Suspicious Token Alerts</b>\n" + "\n".join(f"{a['token']}: {a['reason']}" for a in alerts)

def summarize_wallet_activity():
    summaries = []
    for wallet in TRACKED_WALLETS:
        summaries.append(f"Wallet {wallet[:4]}...{wallet[-4:]} activity summary:\n🟢 2 Buys, 🔴 1 Sell in last 24h")
    return "🧁 <b>Wallet Watchlist</b>\n" + "\n\n".join(summaries)

def track_position():
    value = 3457.91
    cost_basis = 2090.00
    breakeven_price = 0.0002
    return (
        "📈 <b>PnL Tracker</b>\n"
        f"💵 Value: ${value:,.2f}\n"
        f"🧮 PnL: ${value - cost_basis:,.2f}\n"
        f"⚖️ Breakeven Price: ${breakeven_price:.4f}"
    )
