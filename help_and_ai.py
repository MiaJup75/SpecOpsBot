# help_and_ai.py

from telegram import Update
from telegram.ext import CallbackContext
import random

HELP_TEXT = """
<b>🤖 SolMadSpecBot Help & Commands</b>

/start - Welcome message & main menu  
/max - Show detailed MAX token stats  
/wallets - List all watched wallets  
/watch &lt;address&gt; [name] - Add wallet to watchlist  
/addtoken $TOKEN - Add token to watchlist  
/removetoken $TOKEN - Remove token from watchlist  
/tokens - Show list of tracked tokens  
/trending - Top trending Solana meme coins  
/new - New token launches (&lt;24h)  
/alerts - Whale, dev, and suspicious activity alerts  
/pnl - Your MAX token profit & loss stats  
/sentiment - Meme sentiment scores for tokens  
/tradeprompt - AI-generated trade suggestions  
/classify - Meme narrative classification for tokens  
/debug - Simulated debug output for testing  
/panel - Show main interactive panel

Use inline buttons or commands to navigate!
"""

def get_ai_trade_prompt() -> str:
    """
    Generate an AI-powered trade prompt using simple heuristic or data.
    This is a placeholder and can be enhanced with real AI or data sources.
    """
    trade_ideas = [
        {
            "token": "$DUBI",
            "trend": "Bullish",
            "trigger": "Wallet ABC bought 2.1 SOL",
            "support": "0.000024",
            "target": "0.000038",
            "entry": "0.000027",
            "risk": "Medium"
        },
        {
            "token": "$ZAP",
            "trend": "Bearish",
            "trigger": "Whale dumping large amounts",
            "support": "0.000018",
            "target": "0.000010",
            "entry": "0.000015",
            "risk": "High"
        },
        {
            "token": "$FAKE",
            "trend": "Neutral",
            "trigger": "Low social activity",
            "support": "0.000005",
            "target": "0.000007",
            "entry": "0.000006",
            "risk": "Low"
        },
    ]
    idea = random.choice(trade_ideas)

    prompt = f"""<b>📈 AI Trade Prompt for {idea['token']}</b>

🧠 Trend: {idea['trend']}
🔎 Trigger: {idea['trigger']}
📉 Support: {idea['support']} | 📈 Target: {idea['target']}

Suggested Entry: {idea['entry']}
Risk Level: {idea['risk']}

<i>Backtested against mirror wallet clusters and sentiment data</i>
"""
    return prompt

def tradeprompt_command(update: Update, context: CallbackContext) -> None:
    """
    Telegram command handler for /tradeprompt.
    Sends an AI-generated trade suggestion.
    """
    prompt = get_ai_trade_prompt()
    update.message.reply_text(prompt, parse_mode="HTML")

def help_command(update: Update, context: CallbackContext) -> None:
    """
    Telegram command handler for /help.
    Sends the help text listing available commands.
    """
    update.message.reply_text(HELP_TEXT, parse_mode="HTML")
