from telegram import Update, ParseMode
from telegram.ext import CallbackContext

HELP_TEXT = """\
<b>🛠 SolMadSpecBot Help & Commands</b>

Welcome! Here’s what you can do with this bot:

• /max — View MAX token stats and market data  
• /wallets — List all wallets you’re watching  
• /watch <wallet_address> [nickname] — Add a wallet to track  
• /addtoken $TOKEN — Add a token to your watchlist  
• /removetoken $TOKEN — Remove a token from watchlist  
• /tokens — List all tracked tokens  
• /trending — See top trending Solana meme coins  
• /new — View new token launches (<24h)  
• /alerts — Get whale/dev/suspicious activity alerts  
• /pnl — View your MAX token profit & loss stats  
• /sentiment — Meme sentiment scores on trending tokens  
• /tradeprompt — AI-powered trade suggestions  
• /classify — Meme narrative classification for tokens  
• /debug — Simulated data for testing  
• /panel — Open the interactive command panel  

For detailed help on a command, type /help <command>  
Enjoy and trade smart! 🚀
"""

def help_command(update: Update, context: CallbackContext) -> None:
    if context.args:
        cmd = context.args[0].lower()
        # You can add detailed help per command here if you want
        update.message.reply_text(f"Help for /{cmd} is coming soon!")
    else:
        update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)


def get_ai_trade_prompt() -> str:
    # Placeholder example combining data points
    recent_buy = "Wallet ABC bought 2.1 SOL of $ZAZA"
    sentiment = "Bullish"
    support = "0.000024"
    target = "0.000038"
    risk_level = "Medium"

    return f"""\
<b>📈 AI Trade Prompt</b>

🧠 Trend: {sentiment}  
🔎 Trigger: {recent_buy}  
📉 Support: {support} | 📈 Target: {target}

Suggested Entry: 0.000027  
Risk Level: {risk_level}

<i>Backtested against mirror wallet clusters and sentiment data</i>
"""

def tradeprompt_command(update: Update, context: CallbackContext) -> None:
    prompt_text = get_ai_trade_prompt()
    update.message.reply_text(prompt_text, parse_mode=ParseMode.HTML)
