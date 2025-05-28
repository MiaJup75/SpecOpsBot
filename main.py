import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
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
from trade_commands import view_limits_command, set_limits_command, trade_history_command

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
        [InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')],
        [InlineKeyboardButton("📈 View Limits", callback_data='viewlimits'),
         InlineKeyboardButton("⚙️ Set Limits", callback_data='setlimits')],
        [InlineKeyboardButton("📜 Trade History", callback_data='tradehistory')]
    ])

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """<b>👋 Welcome to SolMadSpecBot!</b>

Use the buttons below or type:
/max /wallets /trending  
/new /alerts /debug  
/pnl /sentiment /tradeprompt /classify  
/watch &lt;wallet&gt; /addtoken $TOKEN /tokens  
/viewlimits /setlimit /tradehistory

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
        'max': get_max_token_stats,
        'wallets': get_wallet_summary,
        'trending': get_trending_coins,
        'new': get_new_tokens,
        'alerts': get_suspicious_activity_alerts,
        'pnl': get_pnl_report,
        'sentiment': get_sentiment_scores,
        'tradeprompt': get_trade_prompt,
        'classify': get_narrative_classification,
        'viewlimits': lambda: "Use /viewlimits command to see your current trade limits.",
        'setlimits': lambda: "Use /setlimit <daily_sell_limit> <stop_loss_pct> to set your trade limits.",
        'tradehistory': lambda: "Use /tradehistory <TOKEN_SYMBOL> to view your trade history."
    }

    if command in func_map:
        result = func_map[command]()
        context.bot.send_message(chat_id=query.message.chat.id, text=result, parse_mode=ParseMode.HTML)
    else:
        context.bot.send_message(chat_id=query.message.chat.id, text="Unknown command", parse_mode=ParseMode.HTML)

def watch_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text("Usage: /watch <wallet_address> [nickname]")
        return
    address = context.args[0]
    label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
    try:
        add_wallet(label, address)
        update.message.reply_text(f"✅ Watching wallet:\n<code>{address}</code>\nNickname: {label}", parse_mode=ParseMode.HTML)
    except Exception:
        update.message.reply_text("⚠️ Error adding wallet.")

def wallets_command(update: Update, context: CallbackContext) -> None:
    wallets = get_wallets()
    if not wallets:
        update.message.reply_text("No wallets being tracked.")
        return
    msg = "<b>👛 Watched Wallets</b>\n" + "\n".join([f"• {label}\n<code>{addr}</code>" for label, addr in wallets])
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def addtoken_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text("Usage: /addtoken $TOKEN")
        return
    symbol = context.args[0].lstrip("$")
    try:
        add_token(symbol)
        update.message.reply_text(f"✅ Watching token: ${symbol.upper()}")
    except Exception:
        update.message.reply_text("⚠️ Error adding token.")

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
    symbol = context.args[0].lstrip("$")
    try:
        remove_token(symbol)
        update.message.reply_text(f"✅ Removed token: ${symbol.upper()}")
    except Exception:
        update.message.reply_text("⚠️ Error removing token.")

def debug_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(simulate_debug_output(), parse_mode=ParseMode.HTML)

# Trade commands
dispatcher.add_handler(CommandHandler("viewlimits", view_limits_command))
dispatcher.add_handler(CommandHandler("setlimit", set_limits_command))
dispatcher.add_handler(CommandHandler("tradehistory", trade_history_command))

# Regular commands
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
        BotCommand("panel", "Show the main panel"),
        BotCommand("viewlimits", "View your trade limits"),
        BotCommand("setlimit", "Set daily sell limit and stop loss %"),
        BotCommand("tradehistory", "View your trade history for a token")
    ])
    app.run(host='0.0.0.0', port=PORT)
