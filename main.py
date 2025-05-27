import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from flask import Flask, request
import os
import html

from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens, remove_wallet, remove_token
from apscheduler.schedulers.background import BackgroundScheduler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

# --- Inline Keyboard --- #
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Start", callback_data='start'),
         InlineKeyboardButton("❓ Help", callback_data='help')],
        [InlineKeyboardButton("💰 MAX", callback_data='max'),
         InlineKeyboardButton("👛 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("📈 Trending", callback_data='trending'),
         InlineKeyboardButton("🆕 New", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts'),
         InlineKeyboardButton("📊 PnL", callback_data='pnl')],
        [InlineKeyboardButton("🔍 Sentiment", callback_data='sentiment'),
         InlineKeyboardButton("🤖 AI Trade", callback_data='tradeprompt')],
        [InlineKeyboardButton("📦 Meme Classification", callback_data='classify'),
         InlineKeyboardButton("🐞 Debug", callback_data='debug')],
        [InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
         InlineKeyboardButton("➖ Remove Wallet", switch_inline_query_current_chat='/removewallet ')],
        [InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $'),
         InlineKeyboardButton("❌ Remove Token", switch_inline_query_current_chat='/removetoken $')],
        [InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')],
        [InlineKeyboardButton("⚙️ Panel", callback_data='panel')]
    ])

# --- Command Handlers --- #

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

    func_map = {
        'start': lambda: "Use /start to see the main menu.",
        'help': lambda: HELP_TEXT,
        'max': get_max_token_stats,
        'wallets': get_wallets_text,
        'trending': get_trending_coins,
        'new': get_new_tokens,
        'alerts': get_suspicious_activity_alerts,
        'pnl': get_pnl_report,
        'sentiment': get_sentiment_scores,
        'tradeprompt': get_trade_prompt,
        'classify': get_narrative_classification,
        'debug': simulate_debug_output,
        'panel': lambda: "Use /panel to see the control panel."
    }

    response = func_map.get(command, lambda: "Unknown command")()
    query.edit_message_text(response, parse_mode=ParseMode.HTML)

def get_wallets_text():
    wallets = get_wallets()
    if not wallets:
        return "No wallets currently tracked."

    lines = ["<b>👛 Watched Wallets</b>"]
    for label, addr in wallets:
        safe_label = html.escape(label)
        safe_addr = html.escape(addr)
        lines.append(f"• {safe_label}\n<code>{safe_addr}</code>")
    return "\n".join(lines)

def watch_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) < 1:
            update.message.reply_text("Usage: /watch <wallet_address> [nickname]", parse_mode=ParseMode.HTML)
            return
        address = context.args[0]
        label = " ".join(context.args[1:]) if len(context.args) > 1 else address[:6] + "..."
        add_wallet(label, address)
        update.message.reply_text(f"✅ Watching wallet:\n<b>{html.escape(label)}</b>\n<code>{html.escape(address)}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error adding wallet: {e}")
        update.message.reply_text("⚠️ Error adding wallet.")

def removewallet_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /removewallet <wallet_address>", parse_mode=ParseMode.HTML)
            return
        address = context.args[0]
        remove_wallet(address)
        update.message.reply_text(f"❌ Removed wallet:\n<code>{html.escape(address)}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error removing wallet: {e}")
        update.message.reply_text("⚠️ Error removing wallet.")

def wallets_command(update: Update, context: CallbackContext) -> None:
    text = get_wallets_text()
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

def addtoken_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /addtoken $TOKEN")
            return
        symbol = context.args[0].lstrip("$")
        add_token(symbol)
        update.message.reply_text(f"✅ Watching token: ${html.escape(symbol.upper())}")
    except Exception as e:
        logger.error(f"Error adding token: {e}")
        update.message.reply_text("⚠️ Error adding token.")

def removetoken_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /removetoken $TOKEN")
            return
        symbol = context.args[0].lstrip("$")
        remove_token(symbol)
        update.message.reply_text(f"❌ Removed token: ${html.escape(symbol.upper())}")
    except Exception as e:
        logger.error(f"Error removing token: {e}")
        update.message.reply_text("⚠️ Error removing token.")

def tokens_command(update: Update, context: CallbackContext) -> None:
    tokens = get_tokens()
    if not tokens:
        update.message.reply_text("No tokens currently tracked.")
        return
    token_list = "\n".join([f"• ${html.escape(t)}" for t in tokens])
    update.message.reply_text(f"<b>📋 Watched Tokens</b>\n{token_list}", parse_mode=ParseMode.HTML)

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("panel", panel_command))
dispatcher.add_handler(CommandHandler("max", lambda u, c: u.message.reply_text(get_max_token_stats(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("watch", watch_command))
dispatcher.add_handler(CommandHandler("removewallet", removewallet_command))
dispatcher.add_handler(CommandHandler("addtoken", addtoken_command))
dispatcher.add_handler(CommandHandler("removetoken", removetoken_command))
dispatcher.add_handler(CommandHandler("tokens", tokens_command))
dispatcher.add_handler(CommandHandler("trending", lambda u, c: u.message.reply_text(get_trending_coins(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("new", lambda u, c: u.message.reply_text(get_new_tokens(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("alerts", lambda u, c: u.message.reply_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("debug", lambda u, c: u.message.reply_text(simulate_debug_output(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("pnl", lambda u, c: u.message.reply_text(get_pnl_report(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("sentiment", lambda u, c: u.message.reply_text(get_sentiment_scores(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("tradeprompt", lambda u, c: u.message.reply_text(get_trade_prompt(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("classify", lambda u, c: u.message.reply_text(get_narrative_classification(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# Scheduler job
def send_daily_report(bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: send_daily_report(dispatcher.bot), 'cron', hour=9, minute=0, timezone='Asia/Bangkok')
scheduler.start()

# Webhook setup
@app.route('/')
def index():
    return "SolMadSpecBot is running."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'ok'

# Run app
if __name__ == '__main__':
    init_db()
    updater.bot.set_my_commands([
        BotCommand("start", "Show welcome message and buttons"),
        BotCommand("panel", "Show control panel"),
        BotCommand("max", "Show MAX token stats"),
        BotCommand("wallets", "List all watched wallets"),
        BotCommand("watch", "Add a new wallet to watch"),
        BotCommand("removewallet", "Remove a wallet from watchlist"),
        BotCommand("addtoken", "Add a token to watch"),
        BotCommand("removetoken", "Remove a token from watchlist"),
        BotCommand("tokens", "List all tracked tokens"),
        BotCommand("trending", "View top trending meme coins"),
        BotCommand("new", "Show new token launches"),
        BotCommand("alerts", "Show whale/dev/suspicious alerts"),
        BotCommand("pnl", "Check your MAX token PnL"),
        BotCommand("sentiment", "See meme sentiment scores"),
        BotCommand("tradeprompt", "AI-generated trade idea"),
        BotCommand("classify", "Classify token narratives"),
        BotCommand("debug", "Run simulated debug outputs")
    ])
    app.run(host='0.0.0.0', port=PORT)
