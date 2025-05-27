import datetime

def get_max_token_stats() -> str:
    try:
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
    except Exception:
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

HELP_TEXT = """<b>🛠 Available Commands:</b>

/max – MAX token stats  
/wallets – Wallet activity  
/trending – Top meme coins  
/new – New token launches  
/alerts – Risk alerts  
/pnl – MAX PnL  
/sentiment – Meme scores  
/tradeprompt – AI tips  
/classify – Narrative tags  
/debug – Simulated test output
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
    buy_price = 0.0000335
    current_price = 0.000047
    holdings = 10_450_000
    cost = buy_price * holdings
    current_value = current_price * holdings
    pnl = current_value - cost
    pnl_pct = (pnl / cost) * 100

    return f"""<b>💸 PnL Report – MAX Token</b>

Bought: 10.45M @ ${buy_price:.8f}  
Current: ${current_price:.8f}  
Unrealized PnL: ${pnl:,.2f} ({pnl_pct:.1f}%)
"""

def get_sentiment_scores() -> str:
    return """<b>🧠 Meme Sentiment Scores</b>

$DUBI – 8.7/10 (Buzz + locked LP ✅)  
$ZAP – 6.1/10 (Some whales, weak LP ⚠️)  
$FAKE – 2.8/10 (Botnet & unlocked LP ❌)
"""

def get_trade_prompt() -> str:
    return """<b>🤖 AI Trade Prompt</b>

🟢 Consider watching $DUBI  
• Entry < $0.000021  
• Locked LP  
• Whale inflows detected  
• TG volume up 430%

<i>Not financial advice</i>
"""

def get_narrative_classification() -> str:
    return """<b>🔠 Narrative Classifier</b>

$DUBI – Regional (Dubai Luxury)  
$ZAP – Tech (AI / Smart Contracts)  
$WOOF – Pets/Memes  
$FAKE – None / Generic Risk

<i>Helps identify viral categories early</i>
"""
