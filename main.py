import logging
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand
)
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
)
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens, remove_token
from price_alerts import check_price_alerts
from stealth_launch import scan_new_tokens
from wallet_mirror import check_wallet_mirror
from botnet_detection import check_botnet_alerts
from wallet import Wallet

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

wallet = Wallet()  # Initialize your wallet object here

# --- Inline Keyboard for Main Menu with Explanations --- #
def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💰 MAX Token Stats", callback_data='max'),
            InlineKeyboardButton("👛 Wallets Watchlist", callback_data='wallets')
        ],
        [
            InlineKeyboardButton("📈 Trending Coins", callback_data='trending'),
            InlineKeyboardButton("🆕 New Tokens", callback_data='new')
        ],
        [
            InlineKeyboardButton("🚨 Alerts", callback_data='alerts'),
            InlineKeyboardButton("📊 PnL Report", callback_data='pnl')
        ],
        [
            InlineKeyboardButton("🧠 Meme Sentiment", callback_data='sentiment'),
            InlineKeyboardButton("🤖 AI Trade Prompt", callback_data='tradeprompt')
        ],
        [
            InlineKeyboardButton("🔠 Meme Classification", callback_data='classify')
        ],
        [
            InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
            InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $')
        ],
        [
            InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens'),
            InlineKeyboardButton("⚙️ Sync Tokens", callback_data='sync')
        ],
        [
            InlineKeyboardButton("🤖 Auto Buy", switch_inline_query_current_chat='/autobuy $')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Command Handlers --- #

def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "<b>👋 Welcome to SolMadSpecBot!</b>\n\n"
        "Use the buttons below or type commands to interact:\n"
        "/max - MAX token stats\n"
        "/wallets - Watched wallets\n"
        "/trending - Top trending meme coins\n"
        "/new - New tokens launched recently\n"
        "/alerts - Whale/dev/LP alerts\n"
        "/pnl - MAX token profit & loss\n"
        "/sentiment - Meme sentiment scores\n"
        "/tradeprompt - AI-based trade suggestions\n"
        "/classify - Meme token classifications\n"
        "/watch <wallet> - Add wallet to watchlist\n"
        "/addtoken $TOKEN - Add token to watchlist\n"
        "/tokens - View tracked tokens\n"
        "/autobuy $TOKEN <amount> - Auto buy tokens\n"
        "/sync - Sync trending tokens list\n"
        "/debug - Simulated debug outputs\n\n"
        "Daily reports sent at 9AM Bangkok time (GMT+7)."
    )
    update.message.reply_text(
        welcome_text,
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
    cmd = query.data

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
        'sync': lambda: "Syncing trending tokens list... (feature in progress)"
    }

    response = func_map.get(cmd, lambda: "Unknown command or feature coming soon.")()
    query.edit_message_text(text=response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

def watch_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text("Usage: /watch <wallet_address> [optional nickname]")
        return
    address = context.args[0]
    label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
    try:
        add_wallet(label, address)
        update.message.reply_text(f"✅ Now watching wallet:\n<label>{label}</label>\n<code>{address}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        update.message.reply_text(f"⚠️ Error adding wallet: {e}")

def wallets_command(update: Update, context: CallbackContext) -> None:
    wallets = get_wallets()
    if not wallets:
        update.message.reply_text("No wallets being tracked.")
        return
    msg = "<b>👛 Watched Wallets</b>\n\n" + "\n\n".join([f"• <b>{label}</b>\n<code>{addr}</code>" for label, addr in wallets])
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def addtoken_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text("Usage: /addtoken $TOKEN")
        return
    symbol = context.args[0].lstrip("$").upper()
    try:
        add_token(symbol)
        update.message.reply_text(f"✅ Now watching token: ${symbol}")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error adding token: {e}")

def tokens_command(update: Update, context: CallbackContext) -> None:
    tokens = get_tokens()
    if not tokens:
        update.message.reply_text("No tokens being watched.")
        return
    token_list = "\n".join([f"• ${t}" for t in tokens])
    update.message.reply_text(f"<b>📋 Watched Tokens</b>\n{token_list}", parse_mode=ParseMode.HTML)

def removetoken_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text("Usage: /removetoken $TOKEN")
        return
    symbol = context.args[0].lstrip("$").upper()
    try:
        remove_token(symbol)
        update.message.reply_text(f"✅ Removed token: ${symbol}")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error removing token: {e}")

def autobuy_command(update: Update, context: CallbackContext) -> None:
    # Placeholder - implement actual buy logic in wallet.py and hook here
    if len(context.args) < 2:
        update.message.reply_text("Usage: /autobuy $TOKEN <amount>")
        return
    token = context.args[0].lstrip("$").upper()
    amount = context.args[1]
    update.message.reply_text(f"Attempting to auto-buy {amount} of ${token}...\nFeature coming soon!")

def sync_command(update: Update, context: CallbackContext) -> None:
    # Placeholder for syncing trending tokens
    update.message.reply_text("Syncing trending tokens... Feature coming soon!")

def debug_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(simulate_debug_output(), parse_mode=ParseMode.HTML)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

# --- Register Command Handlers --- #

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("panel", panel_command))
dispatcher.add_handler(CommandHandler("max", lambda u, c: u.message.reply_text(get_max_token_stats(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("watch", watch_command))
dispatcher.add_handler(CommandHandler("addtoken", addtoken_command))
dispatcher.add_handler(CommandHandler("tokens", tokens_command))
dispatcher.add_handler(CommandHandler("removetoken", removetoken_command))
dispatcher.add_handler(CommandHandler("trending", lambda u, c: u.message.reply_text(get_trending_coins(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("new", lambda u, c: u.message.reply_text(get_new_tokens(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("alerts", lambda u, c: u.message.reply_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("debug", debug_command))
dispatcher.add_handler(CommandHandler("pnl", lambda u, c: u.message.reply_text(get_pnl_report(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("sentiment", lambda u, c: u.message.reply_text(get_sentiment_scores(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("tradeprompt", lambda u, c: u.message.reply_text(get_trade_prompt(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("classify", lambda u, c: u.message.reply_text(get_narrative_classification(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("autobuy", autobuy_command))
dispatcher.add_handler(CommandHandler("sync", sync_command))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# --- Scheduled Jobs --- #

scheduler = BackgroundScheduler()

# Daily report at 9AM Bangkok time (using pytz timezone)
from pytz import timezone
bangkok_tz = timezone("Asia/Bangkok")

scheduler.add_job(lambda: updater.bot.send_message(chat_id=CHAT_ID, text=get_full_daily_report(), parse_mode=ParseMode.HTML),
                  'cron', hour=9, minute=0, timezone=bangkok_tz)

scheduler.add_job(lambda: check_price_alerts(updater.bot), 'interval', minutes=5, timezone=bangkok_tz)
scheduler.add_job(lambda: scan_new_tokens(updater.bot), 'interval', minutes=5, timezone=bangkok_tz)
scheduler.add_job(lambda: check_wallet_mirror(updater.bot), 'interval', minutes=10, timezone=bangkok_tz)
scheduler.add_job(lambda: check_botnet_alerts(updater.bot), 'interval', minutes=10, timezone=bangkok_tz)

scheduler.start()

# --- Webhook Setup --- #

@app.route('/')
def index():
    return "SolMadSpecBot is running."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'ok'

# Set webhook on startup
updater.bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")

# --- Main entry point --- #
if __name__ == '__main__':
    init_db()
    # Register bot commands for better UX
    updater.bot.set_my_commands([
        BotCommand("start", "Show welcome message and buttons"),
        BotCommand("max", "Show MAX token stats"),
        BotCommand("wallets", "List all watched wallets"),
        BotCommand("watch", "Add a new wallet to watch"),
        BotCommand("addtoken", "Add a token to watch"),
        BotCommand("tokens", "List all tracked tokens"),
        BotCommand("removetoken", "Remove a token from watchlist"),
        BotCommand("trending", "View top trending meme coins"),
        BotCommand("new", "Show new token launches"),
        BotCommand("alerts", "Show whale/dev/suspicious alerts"),
        BotCommand("pnl", "Check your MAX token PnL"),
        BotCommand("sentiment", "See meme sentiment scores"),
        BotCommand("tradeprompt", "AI-generated trade idea"),
        BotCommand("classify", "Classify token narratives"),
        BotCommand("autobuy", "Auto-buy tokens"),
        BotCommand("sync", "Sync trending tokens list"),
        BotCommand("help", "Show help information")
    ])
    app.run(host='0.0.0.0', port=PORT)
