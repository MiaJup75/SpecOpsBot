import requests
from config import config


def fetch_max_token_data():
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        response = requests.get(url)
        data = response.json()["pair"]

        price = float(data["priceUsd"])
        market_cap = round(float(data.get("marketCap", 0)))
        volume = round(float(data["volume"]["h24"]), 2)
        fdv = round(float(data.get("fdv", 0)))
        buys = data["txns"]["h24"]["buys"]
        sells = data["txns"]["h24"]["sells"]
        liquidity = round(float(data["liquidity"]["usd"]), 2)
        price_change = data["priceChange"]["h24"]
        launch_timestamp = int(data.get("pairCreatedAt", 0)) // 1000
        link = data["url"]

        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${price}
🏛️ Market Cap: ${market_cap}
📉 Volume (24h): ${volume}
🏦 FDV: ${fdv}
📊 Buys: {buys} | Sells: {sells}
💧 Liquidity: ${liquidity}
📈 24H Change: {price_change}%
🕐 Launch Time: <code>{launch_timestamp}</code>
🔗 <a href="{link}">View on Dexscreener</a>"""
        return message
    except Exception as e:
        return f"Error fetching MAX token data: {e}"


def fetch_trending_tokens():
    # Placeholder: Replace with real API integration
    message = """🚀 <b>Trending Solana Meme Coins</b>
1. 🐸 Frogcoin – $0.00321 – Vol: $102,000
2. 🐶 WoofToken – $0.00093 – Vol: $88,432
3. 💎 SolGems – $0.45 – Vol: $72,312
4. 🐍 Snek – $0.00012 – Vol: $69,900
5. 🦄 UniSol – $0.021 – Vol: $55,014"""
    return message


def fetch_new_tokens():
    # Placeholder: Replace with real logic or API call
    message = """🆕 <b>New Token Launches (<12h)</b>
• <code>0xabc...123</code> – LP: $12.3K – Locked: ✅
• <code>0xdef...456</code> – LP: $8.9K – Locked: ❌
• <code>0x789...789</code> – LP: $20.5K – Locked: ✅"""
    return message


def check_suspicious_activity():
    # Placeholder: Replace with real analysis
    message = """⚠️ <b>Suspicious Activity Detected</b>
• Dev Wallet removed 90% LP from TokenX
• Whale Wallet sold $18K of PEPE_INU
• Bot activity spiked for SOLPUNK"""
    return message


def send_target_alerts():
    # Example target triggers
    message = """🎯 <b>Target Price Alerts</b>
• MAX approaching $0.00040 (Sell Zone)
• PEPE_INU broke support level at $0.00009
• SNEK resistance at $0.00015 breached"""
    return message


def summarize_wallet_activity():
    # Placeholder: Summary for Tier 2
    message = """👛 <b>Wallet Activity Summary</b>
• Wallet 1: +3 buys / -1 sell
• Wallet 2: +1 buy / -2 sells
• Wallet 3: No recent activity"""
    return message


def send_wallet_activity():
    return summarize_wallet_activity()


def track_position():
    return """📈 <b>PnL Tracker</b>
• MAX: Avg Buy = $0.00028 | Current = $0.00033
• Unrealized Gain: +18%
• Break-even: $0.00029"""
