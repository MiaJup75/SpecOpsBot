import requests
from datetime import datetime
from db import get_tokens

def get_trending_coins():
    return "🔥 <b>Trending Solana Meme Coins</b>\n• Coin 1\n• Coin 2\n• Coin 3"

def get_new_tokens():
    return "🆕 <b>New Token Launches</b>\n• Token A\n• Token B\n• Token C"

def get_suspicious_activity_alerts():
    return "🚨 <b>Suspicious Activity Alerts</b>\n• Whale sold XYZ\n• Dev pulled LP on Token Q"

def simulate_debug_output():
    return "🛠️ <b>Simulated Debug Output</b>\n- Trending: OK\n- New Tokens: OK\n- Alerts: OK"

def get_wallet_summary():
    return "👛 <b>Watched Wallets</b>\n• Phantom Wallet\n• Trojan Wallet"

def get_pnl_report():
    return "📊 <b>PnL Report</b>\n• TokenA: +15%\n• TokenB: -8%"

def get_sentiment_scores():
    return "🧠 <b>Meme Sentiment Scores</b>\n• TokenA: 🚀\n• TokenB: 🐢"

def get_trade_prompt():
    return "🤖 <b>AI Trade Prompt</b>\nSuggest buying TokenX based on volume/sentiment."

def get_narrative_classification():
    return "🔠 <b>Meme Narrative Classifier</b>\n• TokenX: 'AI'\n• TokenY: 'DOGE'
"

def get_full_daily_report():
    return f"""
<b>🛰️ SpecOpsBot Daily Report</b>

{get_trending_coins()}

{get_new_tokens()}

{get_suspicious_activity_alerts()}

{get_wallet_summary()}

{get_pnl_report()}

<i>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""

HELP_TEXT = """
<b>SpecOpsBot Help</b>
/start – Show welcome panel
/wallets – List tracked wallets
/watch <wallet> – Add a wallet
/addtoken <TOKEN> – Track a token
/removetoken <TOKEN> – Untrack a token
/tokens – View tracked tokens
/trending – View top trending
/new – Show recent launches
/alerts – Suspicious activity
/pnl – View profit & loss
/sentiment – Meme mood
/tradeprompt – AI trade ideas
/classify – Meme themes
/debug – Test all systems
/panel – Main menu
"""
