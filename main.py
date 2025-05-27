import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
)
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens, remove_wallet, remove_token

from stealth_radar import scan_stealth_launches
from price_alerts import check_price_alerts
from botnet import detect_botnet_activity
from mirror_watch import check_mirror_trades
from friend_wallet_sync import sync_friend_wallets

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Main menu buttons and submenus
MAIN_MENU = [
    [InlineKeyboardButton("📊 Market Info", callback_data='menu_market')],
    [InlineKeyboardButton("👛 Watchlists", callback_data='menu_watchlists')],
    [InlineKeyboardButton("🚨 Alerts", callback_data='menu_alerts')],
    [InlineKeyboardButton("🤖 AI & Extras", callback_data='menu_ai')],
    [InlineKeyboardButton("⚙️ Help / Settings", callback_data='menu_help')]
]

SUBMENUS = {
    'menu_market': [
        [InlineKeyboardButton("/max", callback_data='max')],
        [InlineKeyboardButton("/trending", callback_data='trending')],
        [InlineKeyboardButton("/new", callback_data='new')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_main')]
    ],
    'menu_watchlists': [
        [InlineKeyboardButton("/wallets", callback_data='wallets')],
        [InlineKeyboardButton("/watch", callback_data='watch')],
        [InlineKeyboardButton("/removewallet", callback_data='removewallet')],
        [InlineKeyboardButton("/tokens", callback_data='tokens')],
        [InlineKeyboardButton("/addtoken", callback_data='addtoken')],
        [InlineKeyboardButton("/removetoken", callback_data='removetoken')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_main')]
    ],
    'menu_alerts': [
        [InlineKeyboardButton("/alerts", callback_data='alerts')],
        [InlineKeyboardButton("/pnl", callback_data='pnl')],
        [InlineKeyboardButton("/pricealerts", callback_data='pricealerts')],
        [InlineKeyboardButton("/stealth", callback_data='stealth')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_main')]
    ],
    'menu_ai': [
        [InlineKeyboardButton("/sentiment", callback_data='sentiment')],
        [InlineKeyboardButton("/tradeprompt", callback_data='tradeprompt')],
        [InlineKeyboardButton("/classify", callback_data='classify')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_main')]
    ],
    'menu_help': [
        [InlineKeyboardButton("/help", callback_data='help')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_main')]
    ],
}

def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "👋 <b>Welcome to SolMadSpecBot!</b>\n\n"
        "Use the buttons below to navigate through the bot's features.\n\n"
        "Daily summaries at 9AM Bangkok (GMT+7)."
    )
    update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(MAIN_MENU),
        parse_mode=ParseMode.HTML
    )

def send_submenu(update: Update, context: CallbackContext, menu_key: str) -> None:
    submenu_buttons = SUBMENUS.get(menu_key)
    if not submenu_buttons:
        update.callback_query.edit_message_text("Unknown menu.", parse_mode=ParseMode.HTML)
        return
    text_map = {
        'menu_market': "<b>📊 Market Info Commands</b>",
        'menu_watchlists': "<b>👛 Watchlists Commands</b>",
        'menu_alerts': "<b>🚨 Alerts Commands</b>",
        'menu_ai': "<b>🤖 AI & Extras Commands</b>",
        'menu_help': "<b>⚙️ Help & Settings</b>",
    }
    text = text_map.get(menu_key, "Menu")
    update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(submenu_buttons),
        parse_mode=ParseMode.HTML
    )

def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'back_main':
        query.edit_message_text(
            "👋 <b>Welcome back to main menu.</b>",
            reply_markup=InlineKeyboardMarkup(MAIN_MENU),
            parse_mode=ParseMode.HTML
        )
        return

    if data in SUBMENUS:
        send_submenu(update, context, data)
        return

    # Map commands to functions or strings
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
        'debug': simulate_debug_output,
        'watch': lambda: "To add a wallet, use /watch <wallet_address>",
        'removewallet': lambda: "To remove a wallet, use /removewallet <wallet_address>",
        'addtoken': lambda: "To add a token, use /addtoken $TOKEN",
        'removetoken': lambda: "To remove a token, use /removetoken $TOKEN",
        'tokens': lambda: "\n".join([f"• ${t}" for t in get_tokens()]) or "No tokens tracked.",
        'stealth': lambda: "Stealth launch radar is active and will notify you of suspicious launches.",
        'pricealerts': lambda: "Price alerts are active and will notify you on target prices.",
        # add more simple texts or implement commands as needed
    }

    func = func_map.get(data)
    if func:
        if callable(func):
            try:
                text = func()
            except Exception as e:
                logger.error(f"Error in callback {data}: {e}")
                text = "Error processing command."
        else:
            text = func
    else:
        text = "Unknown command."

    query.edit_message_text(text, parse_mode=ParseMode.HTML)

# Wallet and token command handlers (unchanged)
def watch_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /watch <wallet_address>", parse_mode=ParseMode.HTML)
            return
        address = context.args[0]
        label = f"Wallet {address[:4]}...{address[-4:]}"
        add_wallet(label, address)
        update.message.reply_text(f"✅ Watching wallet:\n<code>{address}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error adding wallet: {e}")
        update.message.reply_text("⚠️ Error adding wallet.")

def removewallet_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Usage: /removewallet <wallet_address>")
        return
    address = context.args[0]
    remove_wallet(address)
    update.message.reply_text(f"🗑️ Removed wallet:\n<code>{address}</code>", parse_mode=ParseMode.HTML)

def addtoken_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /addtoken $TOKEN")
            return
        symbol = context.args[0].lstrip("$")
        add_token(symbol)
        update.message.reply_text(f"✅ Watching token: ${symbol.upper()}")
    except Exception:
        update.message.reply_text("⚠️ Error adding token.")

def removetoken_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Usage: /removetoken $TOKEN")
        return
    symbol = context.args[0].lstrip("$")
    remove_token(symbol)
    update.message.reply_text(f"🗑️ Removed token: ${symbol.upper()}")

def tokens_command(update: Update, context: CallbackContext) -> None:
    tokens = get_tokens()
    if not tokens:
        update.message.reply_text("No tokens being watched.")
        return
    token_list = "\n".join([f"• ${t}" for t in tokens])
    update.message.reply_text(f"<b>📋 Watched Tokens</b>\n{token_list}", parse_mode=ParseMode.HTML)

def wallets_command(update: Update, context: CallbackContext) -> None:
    wallets = get_wallets()
    if not wallets:
        update.message.reply_text("No wallets being tracked.")
        return
    msg = "<b>👛 Watched Wallets</b>\n" + "\n".join([f"• {label}\n<code>{addr}</code>" for label, addr in wallets])
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# Help command
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("panel", start))  # panel shows main menu too
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
dispatcher.add_handler(CommandHandler("stealth", lambda u, c: u.message.reply_text("Stealth launch radar is active.", parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("pricealerts", lambda u, c: u.message.reply_text("Price alerts are active.", parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))
dispatcher.add_handler(CommandHandler("help", help_command))

# Scheduler jobs
def send_daily_report(bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
scheduler.add_job(lambda: send_daily_report(dispatcher.bot), 'cron', hour=9, minute=0)
scheduler.add_job(lambda: scan_stealth_launches(dispatcher.bot), 'interval', minutes=5)
scheduler.add_job(lambda: check_price_alerts(dispatcher.bot), 'interval', minutes=1)
scheduler.add_job(lambda: detect_botnet_activity(dispatcher.bot), 'interval', minutes=3)
scheduler.add_job(lambda: check_mirror_trades(dispatcher.bot), 'interval', minutes=3)
scheduler.add_job(lambda: sync_friend_wallets(dispatcher.bot), 'interval', minutes=10)
scheduler.start()

# Webhook routes
@app.route('/')
def index():
    return "SolMadSpecBot is running."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'ok'

# Main app run
if __name__ == '__main__':
    init_db()
    updater.bot.set_my_commands([
        BotCommand(cmd, desc) for cmd, desc in {
            'start': 'Show welcome message and menu',
            'help': 'Show help text',
            'max': 'Show MAX token stats',
            'wallets': 'List all watched wallets',
            'watch': 'Add a new wallet to watch',
            'removewallet': 'Remove wallet from watchlist',
            'addtoken': 'Add a token to watch',
            'removetoken': 'Remove a token from watchlist',
            'tokens': 'List all tracked tokens',
            'trending': 'View top trending meme coins',
            'new': 'Show new token launches',
            'alerts': 'Show whale/dev/suspicious alerts',
            'pnl': 'Check your MAX token PnL',
            'sentiment': 'See meme sentiment scores',
            'tradeprompt': 'AI-generated trade idea',
            'classify': 'Classify token narratives',
            'debug': 'Run simulated debug outputs',
            'stealth': 'Stealth launch radar info',
            'pricealerts': 'Price alert notifications'
        }.items()
    ])
    app.run(host='0.0.0.0', port=PORT)
