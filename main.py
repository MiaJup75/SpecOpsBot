import logging
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ParseMode, BotCommand, Bot
)
from telegram.ext import (
    Updater, CommandHandler, CallbackContext,
    CallbackQueryHandler, Dispatcher
)
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens, remove_token
from price_alerts import check_price_targets
from stealth_launch import scan_new_tokens
from mirror_watch import check_mirror_wallets
from botnet import check_botnet_activity
from wallet import Wallet
from tokens import handle_add_token, handle_tokens, handle_remove_token  # Updated tokens handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher


def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 MAX", callback_data='max'),
         InlineKeyboardButton("👛 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("📈 Trending", callback_data='trending'),
         InlineKeyboardButton("🆕 New", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts'),
         InlineKeyboardButton("📊 PnL", callback_data='pnl')],
        [InlineKeyboardButton("🧠 Meme Sentiment", callback_data='sentiment'),
         InlineKeyboardButton("🤖 Trade Prompt", callback_data='tradeprompt')],
        [InlineKeyboardButton("🔠 Meme Classification", callback_data='classify')],
        [InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
         InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $')],
        [InlineKeyboardButton("📋 View Tokens", callback_data='tokens')]
    ])


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """<b>👋 Welcome to SolMadSpecBot!</b>

Use the buttons below or type:
/max /wallets /trending  
/new /alerts /debug  
/pnl /sentiment /tradeprompt /classify  
/watch &lt;wallet&gt; /addtoken $TOKEN /tokens

Daily updates sent at 9AM Bangkok time (GMT+7).""",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )


def panel_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🔘 <b>SolMadSpecBot Panel</b>\nTap a button below:",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )


def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    command = query.data

    # Map callback commands to functions returning string output
    func_map = {
        'max': get_max_token_stats,
        'wallets': get_wallet_summary,
        'trending': get_trending_coins,
        'new': get_new_tokens,
        'alerts': get_suspicious_activity_alerts,
        'pnl': get_pnl_report,
        'sentiment': get_sentiment_scores,
        'tradeprompt': get_trade_prompt,
        'classify': get_narrative_classification,
        'tokens': lambda: build_token_list_with_buttons(context)
    }

    if command.startswith("token_"):
        # Show detailed info for clicked token symbol, e.g. token_MAX
        token_symbol = command.split("_", 1)[1].upper()
        msg = get_token_detail_text(token_symbol)
        context.bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=ParseMode.HTML)
        return

    func = func_map.get(command)
    if func:
        # Call the function and send result as message
        result = func()
        if isinstance(result, str):
            context.bot.send_message(chat_id=query.message.chat.id, text=result, parse_mode=ParseMode.HTML)
        elif isinstance(result, InlineKeyboardMarkup):
            context.bot.send_message(chat_id=query.message.chat.id, text="Select a token:", reply_markup=result)
        else:
            context.bot.send_message(chat_id=query.message.chat.id, text="Unknown response format.")
    else:
        context.bot.send_message(chat_id=query.message.chat.id, text="Unknown command.")


def build_token_list_with_buttons(context: CallbackContext):
    tokens = get_tokens()
    if not tokens:
        return "<b>No tokens currently tracked.</b>"

    buttons = []
    # Create buttons with callback_data for each token
    for token in tokens:
        buttons.append([InlineKeyboardButton(f"${token}", callback_data=f"token_{token}")])
    return InlineKeyboardMarkup(buttons)


def get_token_detail_text(symbol: str) -> str:
    """Fetch token config and build detail text similar to MAX format."""
    from token_config import get_token_config
    config = get_token_config(symbol)
    if not config:
        return f"⚠️ No data available for token ${symbol}"

    # For demonstration, fetch live price from Dexscreener if pair exists
    import requests
    try:
        pair = config.get("pair")
        if not pair:
            return f"⚠️ No trading pair found for ${symbol}"

        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if "pair" not in data:
            return f"⚠️ Token data unavailable for ${symbol}"

        p = data["pair"]
        price = p["priceUsd"]
        market_cap = float(p.get("marketCap", 0))
        volume = float(p["volume"]["h24"])
        liquidity = float(p["liquidity"]["usd"])
        buys = p["txns"]["h24"]["buys"]
        sells = p["txns"]["h24"]["sells"]
        change = float(p.get("priceChange", {}).get("h24", 0))
        fdv = float(p.get("fdv", 0))
        launch_ts = int(p.get("pairCreatedAt", 0))
        launch_date = "N/A"
        if launch_ts > 0:
            launch_date = datetime.datetime.fromtimestamp(launch_ts / 1000).strftime('%Y-%m-%d %H:%M:%S')

        dex_link = f"https://dexscreener.com/solana/{pair}"

        description = config.get("description", "")

        return f"""
<b>Token: ${symbol} - {description}</b>

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
    except Exception:
        return f"⚠️ Unable to fetch data for ${symbol}"


def watch_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text("Usage: /watch <wallet_address> [nickname]")
        return
    address = context.args[0]
    label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
    try:
        add_wallet(label, address)
        update.message.reply_text(
            f"✅ Watching wallet:\n<code>{address}</code>\nNickname: {label}",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        update.message.reply_text("⚠️ Error adding wallet.")


def wallets_command(update: Update, context: CallbackContext) -> None:
    wallets = get_wallets()
    if not wallets:
        update.message.reply_text("No wallets being tracked.")
        return
    msg = "<b>👛 Watched Wallets</b>\n" + "\n".join([f"• {label}\n<code>{addr}</code>" for label, addr in wallets])
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("panel", panel_command))
dispatcher.add_handler(CommandHandler("max", lambda u, c: u.message.reply_text(get_max_token_stats(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("watch", watch_command))
dispatcher.add_handler(CommandHandler("addtoken", handle_add_token))
dispatcher.add_handler(CommandHandler("tokens", handle_tokens))
dispatcher.add_handler(CommandHandler("removetoken", handle_remove_token))
dispatcher.add_handler(CommandHandler("trending", lambda u, c: u.message.reply_text(get_trending_coins(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("new", lambda u, c: u.message.reply_text(get_new_tokens(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("alerts", lambda u, c: u.message.reply_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("debug", lambda u, c: u.message.reply_text(simulate_debug_output(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("pnl", lambda u, c: u.message.reply_text(get_pnl_report(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("sentiment", lambda u, c: u.message.reply_text(get_sentiment_scores(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("tradeprompt", lambda u, c: u.message.reply_text(get_trade_prompt(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("classify", lambda u, c: u.message.reply_text(get_narrative_classification(), parse_mode=ParseMode.HTML)))

dispatcher.add_handler(CallbackQueryHandler(handle_callback))

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))

jobs = [
    {"func": lambda: scan_new_tokens(updater.bot), "trigger": "interval", "minutes": 5},
    {"func": lambda: check_price_targets(updater.bot), "trigger": "interval", "minutes": 10},
    {"func": lambda: check_mirror_wallets(updater.bot), "trigger": "interval", "minutes": 10},
    {"func": lambda: check_botnet_activity(updater.bot), "trigger": "interval", "minutes": 10},
    {"func": lambda: send_daily_report(updater.bot), "trigger": "cron", "hour": 9, "minute": 0}
]

for job in jobs:
    scheduler.add_job(job["func"], job["trigger"], **{k: v for k, v in job.items() if k not in ["func", "trigger"]})
scheduler.start()


def send_daily_report(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)


@app.route('/')
def index():
    return "SolMadSpecBot is running."


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'ok'


if __name__ == '__main__':
    init_db()
    updater.bot.set_my_commands([
        BotCommand("start", "Show welcome message and buttons"),
        BotCommand("max", "Show MAX token stats"),
        BotCommand("wallets", "List all watched wallets"),
        BotCommand("watch", "Add a new wallet to watch"),
        BotCommand("addtoken", "Add a token to watch"),
        BotCommand("removetoken", "Remove a token from watchlist"),
        BotCommand("tokens", "List all tracked tokens"),
        BotCommand("trending", "View top trending meme coins"),
        BotCommand("new", "Show new token launches"),
        BotCommand("alerts", "Show whale/dev/suspicious alerts"),
        BotCommand("pnl", "Check your MAX token PnL"),
        BotCommand("sentiment", "See meme sentiment scores"),
        BotCommand("tradeprompt", "AI-generated trade idea"),
        BotCommand("classify", "Meme classification of tokens"),
        BotCommand("debug", "Run simulated debug outputs"),
        BotCommand("panel", "Show the main panel")
    ])
    app.run(host='0.0.0.0', port=PORT)
