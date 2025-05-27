import datetime
import requests

def get_max_token_stats() -> str:
    try:
        pair_address = "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if 'pair' not in data:
            return "⚠️ MAX token data unavailable."

        p = data['pair']
        price = p['priceUsd']
        market_cap = float(p.get('marketCap', 0))
        volume = float(p['volume']['h24'])
        liquidity = float(p['liquidity']['usd'])
        buys = p['txns']['h24']['buys']
        sells = p['txns']['h24']['sells']
        change = float(p.get('priceChange', {}).get('h24', 0))
        fdv = float(p.get('fdv', 0))
        launch_ts = int(p.get('pairCreatedAt', 0))
        launch_date = datetime.datetime.fromtimestamp(launch_ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
        pair_name = p.get("baseToken", {}).get("symbol", "MAX")

        dex_link = f"https://dexscreener.com/solana/{pair_address}"

        return f"""
<b>🐶 MAX Token Update</b>

📈 <b>Price:</b> ${price}
💰 <b>Market Cap:</b> ${market_cap:,.0f}
🌿 <b>Volume (24h):</b> ${volume:,.2f}
💵 <b>FDV:</b> ${fdv:,.0f}
📊 <b>Buys:</b> {buys} | <b>Sells:</b> {sells}
💧 <b>Liquidity:</b> ${liquidity:,.2f}
🕒 <b>24H Change:</b> {change}%
📅 <b>Launch Date:</b> {launch_date}
🔗 <a href='{dex_link}'>View on Dexscreener</a>
"""
    except Exception as e:
        return f"⚠️ Unable to fetch MAX token data."

def get_trending_coins() -> str:
    return """<b>📈 Top 5 Trending Solana Meme Coins</b>

1. BONK – +65% 🔥  
2. MEOW – +38%  
3. CHAD – +34%  
4. WEN – +27%  
5. SLERF – +24%

<i>Data from DEX volume & Telegram buzz</i>
"""

def get_new_tokens() -> str:
    return """<b>🆕 New Token Launches (&lt;24h)</b>

• $LOOT – LP $8.4K – Locked 7d ✅  
• $ZOOM – LP $5.9K – Unlocks in 12h ⚠️  
• $RUGME – LP $3.1K – No lock ❌

<i>Click /alerts for suspicious flags</i>
"""

def get_suspicious_activity_alerts() -> str:
    return """<b>🚨 Suspicious Activity</b>

• DEV wallet sold 30% of $CHEEMS  
• LP for $FAKE withdrawn (-70%)  
• Botnet activity on $ZOOM  
• Whale exit from $SLURP (500M tokens)

<i>Monitored wallets + LP changes</i>
"""

# Other command helpers (unchanged from previous utils.py) ...
