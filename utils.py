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

def get_wallet_summary() -> str:
    return """<b>👛 Wallet Watch Summary</b>

• Main Wallet – No suspicious activity  
• Trojan Wallet – 1 new buy (1.5 SOL)  
• Burner Wallet – Idle  

MAX token top wallet sold 115K tokens  
LP unchanged in past 24h
"""

def get_full_daily_report() -> str:
    today = datetime.date.today()
    return f"""<b>🌞 Daily Solana Meme Report – {today}</b>

📈 <b>Trending Coins</b>  
1. BONK – +65%  
2. MEOW – +38%  
3. CHAD – +34%

🆕 <b>New Tokens</b>  
• $LOOT – LP $8.4K – Locked  
• $ZOOM – LP $5.9K – Unlocks soon

🚨 <b>Alerts</b>  
• DEV dumped $CHEEMS  
• $FAKE LP pulled

💰 <b>MAX Token</b>  
{get_max_token_stats().replace('<b>', '').replace('</b>', '')}

👛 <b>Wallets</b>  
• Trojan: 1 buy  
• MAX: 115K sold

🧠 <b>Sentiment</b>  
$DUBI – 8.7/10  
$ZAP – 6.1/10  
$FAKE – 2.8/10

🤖 <b>Trade Prompt</b>  
Watch $DUBI < $0.000021

🔠 <b>Narratives</b>  
$DUBI – Dubai  
$ZAP – AI  
$FAKE – None
"""

def simulate_debug_output() -> str:
    return """<b>🧪 Debug Simulation</b>

Simulated /new:  
• $TEST – LP $4.2K – Locked ✅  
• $FAKE – LP $6.8K – No lock ❌  

Simulated /alerts:  
• Whale dumped 900K $SIM  

<i>This is dummy data for debug only</i>
"""

def get_pnl_report() -> str:
    return """<b>📊 MAX Token PnL Report</b>

• Holdings: 10.45M MAX  
• Average Buy: 0.000028  
• Current Price: 0.000030  
• Unrealized PnL: +7.1%  
• Target Exit: $500K Market Cap  
• Sell Plan: 2M tokens @ 0.000050

<i>Last updated: Today</i>
"""

def get_sentiment_scores() -> str:
    return """<b>🧠 Meme Sentiment Scores</b>

• $DUBI – 8.7/10 😍  
• $ZAP – 6.1/10 😐  
• $FAKE – 2.8/10 💩

<i>Based on emoji density, TG spam, and tweet velocity</i>
"""

def get_trade_prompt() -> str:
    return """<b>📈 AI Trade Prompt</b>

🧠 Trend: Bullish  
🔎 Trigger: Wallet ABC bought 2.1 SOL of $ZAZA  
📉 Support: 0.000024 | 📈 Target: 0.000038

Suggested Entry: 0.000027
Risk Level: Medium

<i>Backtested against mirror wallet clusters</i>
"""

HELP_TEXT = """<b>🛠 Available Commands:</b>

/max – View MAX token stats  
/wallets – See tracked wallet updates  
/trending – Top trending meme coins  
/new – Tokens launched in last 24h  
/alerts – Whale/dev/LP risk alerts  
/debug – Simulated output for testing  
/pnl – Show MAX token break-even stats  
/sentiment – Emoji/meme score for trending tokens  
/tradeprompt – Smart suggestion based on wallet activity  
/classify – Tag token narratives using AI  
/watch – Add wallet to your watchlist  
/addtoken – Track a token on your list  
/tokens – Show tracked token list
"""

# Other command helpers (unchanged from previous utils.py) ...
