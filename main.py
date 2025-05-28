import logging
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
    BotCommand, Bot
)
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
)
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# Import your existing data and logic functions here
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

# === Menus ===

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Tokens & Markets", callback_data='menu_tokens')],
        [InlineKeyboardButton("👛 Wallets & Holdings", callback_data='menu_wallets')],
        [InlineKeyboardButton("🤖 Analytics & AI", callback_data='menu_analytics')],
        [InlineKeyboardButton("💼 Trading & Limits", callback_data='menu_trading')],
        [InlineKeyboardButton("⚙️ Miscellaneous", callback_data='menu_misc')],
    ])

def get_tokens_submenu():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐶 MAX Token", callback_data='token_MAX')],
        [InlineKeyboardButton("📈 Trending Coins", callback_data='trending')],
        [InlineKeyboardButton("🆕 New Tokens", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts')],
        [InlineKeyboardButton("📋 Manage Tokens", callback_data='tokens')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')],
    ])
    text = (
        "<b>Tokens & Markets</b>\n\n"
        "• View MAX token stats\n"
        "• Check trending meme coins\n"
        "• Discover newly launched tokens\n"
        "• View suspicious alerts\n"
        "• Manage your tracked tokens"
    )
    return text, keyboard

def get_wallets_submenu():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👛 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch ')],
        [InlineKeyboardButton("📊 PnL Report", callback_data='pnl')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')],
    ])
    text = (
        "<b>Wallets & Holdings</b>\n\n"
        "• View watched wallets\n"
        "• Add a new wallet to track\n"
        "• Check profit & loss reports"
    )
    return text, keyboard

def get_analytics_submenu():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 Sentiment Scores", callback_data='sentiment')],
        [InlineKeyboardButton("🤖 Trade Prompt", callback_data='tradeprompt')],
        [InlineKeyboardButton("🔠 Classification", callback_data='classify')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')],
    ])
    text = (
        "<b>Analytics & AI</b>\n\n"
        "• Meme sentiment scores\n"
        "• AI trade prompts\n"
        "• Token narrative classification"
    )
    return text, keyboard

def get_trading_submenu():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 Set Limits", callback_data='set_limits')],
        [InlineKeyboardButton("📊 View Limits", callback_data='view_limits')],
        [InlineKeyboardButton("📜 Trade History", callback_data='trade_history')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')],
    ])
    text = (
        "<b>Trading & Limits</b>\n\n"
        "• Set your trade limits\n"
        "• View current limits\n"
        "• Review your trade history"
    )
    return text, keyboard

def get_misc_submenu():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐞 Debug", callback_data='debug')],
        [InlineKeyboardButton("🔄 Panel", callback_data='panel')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')],
    ])
    text = (
        "<b>Miscellaneous</b>\n\n"
        "• Debug simulation output\n"
        "• Show main control panel"
    )
    return text, keyboard

# === Token Detail Viewer ===

def get_token_detail(symbol: str) -> str:
    # You can expand this with API calls or DB info
    if symbol.upper() == "MAX":
        return get_max_token_stats()
    else:
        return f"<b>{symbol.upper()}</b> details not available yet."

# === Command Handlers ===

def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "<b>👋 Welcome to SolMadSpecBot!</b>\n\n"
        "Use the menu below to explore features.\n"
        "Or type commands like /max, /wallets, /tokens.\n"
        "Daily updates sent at 9AM Bangkok time (GMT+7)."
    )
    update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode='HTML')

def panel_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🔘 <b>SolMadSpecBot Panel</b>\nTap a button below:",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'main_menu':
        query.edit_message_text(
            text="🔘 <b>Main Menu</b>\nSelect a category:",
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )
        return

    submenu_map = {
        'menu_tokens': get_tokens_submenu,
        'menu_wallets': get_wallets_submenu,
        'menu_analytics': get_analytics_submenu,
        'menu_trading': get_trading_submenu,
        'menu_misc': get_misc_submenu,
    }

    if data in submenu_map:
        text, keyboard = submenu_map[data]()
        query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')
        return

    if data.startswith("token_"):
        token_symbol = data.split("_", 1)[1]
        detail_text = get_token_detail(token_symbol)
        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Tokens", callback_data='menu_tokens')]
        ])
        query.edit_message_text(text=detail_text, reply_markup=back_button, parse_mode='HTML')
        return

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
        'set_limits': lambda: "Use /setlimit <daily_sell_limit> <stop_loss_pct> to update your limits.",
        'view_limits': lambda: "Use /viewlimits to see your current limits.",
        'trade_history': lambda: "Use /tradehistory <TOKEN> to view your trade history.",
        'debug': simulate_debug_output,
        'panel': lambda: "Use /panel to see the main control panel.",
    }

    if data in func_map:
        result = func_map[data]()
        query.edit_message_text(text=result, parse_mode='HTML')
        return

    query.edit_message_text(text="❓ Unknown command. Please try again.")

# === Commands registration ===

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("panel", panel_command))
dispatcher.add_handler(CommandHandler("max", lambda u, c: u.message.reply_text(get_max_token_stats(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("wallets", lambda u, c: u.message.reply_text(get_wallet_summary(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("trending", lambda u, c: u.message.reply_text(get_trending_coins(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("new", lambda u, c: u.message.reply_text(get_new_tokens(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("alerts", lambda u, c: u.message.reply_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("pnl", lambda u, c: u.message.reply_text(get_pnl_report(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("sentiment", lambda u, c: u.message.reply_text(get_sentiment_scores(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("tradeprompt", lambda u, c: u.message.reply_text(get_trade_prompt(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("classify", lambda u, c: u.message.reply_text(get_narrative_classification(), parse_mode=ParseMode.HTML)))

dispatcher.add_handler(CommandHandler("watch", lambda u, c: u.message.reply_text("Use the menu to add wallets.", parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("addtoken", lambda u, c: u.message.reply_text("Use the menu to add tokens.", parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("tokens", lambda u, c: u.message.reply_text("Use the menu to manage tokens.", parse_mode=ParseMode.HTML)))

dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# === Scheduler setup ===

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
