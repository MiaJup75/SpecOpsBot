import datetime

def get_max_token_stats() -> str:
    try:
        # Example stats from Dexscreener (replace with real fetch)
        price = "0.000047"
        market_cap = "$480K"
        volume = "$55K"
        liquidity = "$72K"
        holders = "1,235"
        last_updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return f"""<b>💰 MAX Token Stats</b>

Price: ${price}
Market Cap: {market_cap}
24h Volume: {volume}
Liquidity: {liquidity}
Holders: {holders}

<i>Last updated: {last_updated}</i>
"""
    except Exception as e:
        return "⚠️ Unable to fetch MAX token data."

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
    return """<b>🆕 New Token Launches (<24h)</b>

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
    return f"""<b>🌞 Daily Solana Meme Report – {datetime.date.today()}</b>

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
Price: $0.000047  
MC: $480K | Vol: $55K  
Liquidity: $72K | Holders: 1,235

👛 <b>Wallets</b>  
• Trojan: 1 buy  
• MAX: 115K sold
"""

HELP_TEXT = """<b>🛠 Available Commands:</b>

/max – View MAX token stats  
/wallets – See tracked wallet updates  
/trending – Top trending meme coins  
/new – Tokens launched in last 24h  
/alerts – Whale/dev/LP risk alerts  
/debug – Simulated output for testing
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
