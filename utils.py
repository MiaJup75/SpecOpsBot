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
