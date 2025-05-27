import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    Dispatcher
)
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler

from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens, remove_wallet, remove_token
from stealth_radar import fetch_new_tokens, filter_suspicious
from price_alerts import check_price_targets
from mirror_watch import monitor_wallets
from botnet import botnet_alerts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """<b>👋 Welcome to SolMadSpecBot!</b>

Use the buttons below or type commands:

/max /wallets /trending  
/new /alerts /debug  
/pnl /sentiment /tradeprompt /classify  
/stealth /mirror /botnet  
/watch &lt;wallet&gt; /addtoken $TOKEN /tokens  
/pricealerts

Daily updates sent at 9AM Bangkok time (GMT+7).""",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

def panel(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🔘 <b>SolMadSpecBot Panel</b>\nTap a button below:",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    command = query.data

    if command in COMMANDS:
        result = COMMANDS[command]['handler'](update, context, silent=True)
    else:
        result = "Unknown command"

    if result:
        try:
            query.edit_message_text(text=result, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Error editing message: {e}")

def watch(update: Update, context: CallbackContext, silent=False) -> str | None:
    try:
        if len(context.args) < 1:
            msg = ("Usage: /watch <wallet_address> [label]\n"
                   "Example: /watch 4FEj7nwm5wZXbMo3zSDiV51eLgbFWgPtFRHATUFpu9As MyWallet")
            if not silent:
                update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return msg
        address = context.args[0]
        label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
        add_wallet(label, address)
        msg = f"✅ Watching wallet:\n<code>{address}</code> as '{label}'"
        if not silent:
            update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        return msg
    except Exception as e:
        logger.error(f"Error adding wallet: {e}")
        if not silent:
            update.message.reply_text("⚠️ Error adding wallet.")
        return None

def wallets(update: Update, context: CallbackContext, silent=False) -> str | None:
    wallets = get_wallets()
    if not wallets:
        msg = "No wallets being tracked."
        if not silent:
            update.message.reply_text(msg)
        return msg
    msg = "<b>👛 Watched Wallets</b>\n" + "\n".join([f"• {label}\n<code>{addr}</code>" for label, addr in wallets])
    if not silent:
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    return msg

def addtoken(update: Update, context: CallbackContext, silent=False) -> str | None:
    try:
        if len(context.args) != 1:
            msg = "Usage: /addtoken $TOKEN"
            if not silent:
                update.message.reply_text(msg)
            return msg
        symbol = context.args[0].lstrip("$")
        add_token(symbol)
        msg = f"✅ Watching token: ${symbol.upper()}"
        if not silent:
            update.message.reply_text(msg)
        return msg
    except Exception as e:
        logger.error(f"Error adding token: {e}")
        if not silent:
            update.message.reply_text("⚠️ Error adding token.")
        return None

def tokens(update: Update, context: CallbackContext, silent=False) -> str | None:
    tokens = get_tokens()
    if not tokens:
        msg = "No tokens being watched."
        if not silent:
            update.message.reply_text(msg)
        return msg
    token_list = "\n".join([f"• ${t}" for t in tokens])
    msg = f"<b>📋 Watched Tokens</b>\n{token_list}"
    if not silent:
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    return msg

# Wrappers for simple commands returning strings
def text_response(fn):
    def wrapper(update, context, silent=False):
        text = fn()
        if not silent:
            update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return text
    return wrapper

max_command = text_response(get_max_token_stats)
trending_command = text_response(get_trending_coins)
new_command = text_response(get_new_tokens)
alerts_command = text_response(get_suspicious_activity_alerts)
debug_command = text_response(simulate_debug_output)
pnl_command = text_response(get_pnl_report)
sentiment_command = text_response(get_sentiment_scores)
tradeprompt_command = text_response(get_trade_prompt)
classify_command = text_response(get_narrative_classification)

def stealth_command(update: Update, context: CallbackContext, silent=False) -> str | None:
    new_tokens = fetch_new_tokens()
    suspicious = filter_suspicious(new_tokens)
    if not suspicious:
        msg = "No suspicious new tokens found in last 30 minutes."
        if not silent:
            update.message.reply_text(msg)
        return msg
    msg = "\n\n".join(
        f"{t['name']} - Liquidity: ${t['liquidity']}, Social: {t['socialSignals']}, Launched: {t['launchTime']}"
        for t in suspicious
    )
    if not silent:
        update.message.reply_text(msg)
    return msg

def mirror_command(update: Update, context: CallbackContext, silent=False) -> str | None:
    monitor_wallets(context.bot)
    msg = "✅ Wallet mirror check triggered."
    if not silent:
        update.message.reply_text(msg)
    return msg

def botnet_command(update: Update, context: CallbackContext, silent=False) -> str | None:
    botnet_alerts(context.bot)
    msg = "✅ Botnet detection triggered."
    if not silent:
        update.message.reply_text(msg)
    return msg

def price_alert_command(update: Update, context: CallbackContext) -> None:
    check_price_targets(context.bot)
    update.message.reply_text("✅ Price targets checked and alerts sent if any.")

# --- Commands config for dynamic registration ---
COMMANDS = {
    "start": {"handler": start, "desc": "Show welcome message and buttons", "button": False},
    "panel": {"handler": panel, "desc": "Show the control panel", "button": False},
    "max": {"handler": max_command, "desc": "Show MAX token stats", "button": True},
    "wallets": {"handler": wallets, "desc": "List all watched wallets", "button": True},
    "watch": {"handler": watch, "desc": "Add a new wallet to watch", "button": False},
    "addtoken": {"handler": addtoken, "desc": "Add a token to watch", "button": False},
    "tokens": {"handler": tokens, "desc": "List all tracked tokens", "button": True},
    "trending": {"handler": trending_command, "desc": "View top trending meme coins", "button": True},
    "new": {"handler": new_command, "desc": "Show new token launches", "button": True},
    "alerts": {"handler": alerts_command, "desc": "Show whale/dev/suspicious alerts", "button": True},
    "debug": {"handler": debug_command, "desc": "Run simulated debug outputs", "button": True},
    "pnl": {"handler": pnl_command, "desc": "Check your MAX token PnL", "button": True},
    "sentiment": {"handler": sentiment_command, "desc": "See meme sentiment scores", "button": True},
    "tradeprompt": {"handler": tradeprompt_command, "desc": "AI-generated trade idea", "button": True},
    "classify": {"handler": classify_command, "desc": "Classify token narratives", "button": True},
    "stealth": {"handler": stealth_command, "desc": "Run stealth launch radar", "button": True},
    "mirror": {"handler": mirror_command, "desc": "Run wallet mirror check", "button": True},
    "botnet": {"handler": botnet_command, "desc": "Run botnet detection", "button": True},
    "pricealerts": {"handler": price_alert_command, "desc": "Check price targets and send alerts", "button": True}
}

def get_main_keyboard():
    buttons = []
    row = []
    for cmd, data in COMMANDS.items():
        if data.get("button", False):
            btn = InlineKeyboardButton(data["desc"].split()[0], callback_data=cmd)
            row.append(btn)
            if len(row) == 2:
                buttons.append(row)
                row = []
    if row:
        buttons.append(row)

    # Add wallet/token add buttons at bottom
    buttons.append([
        InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
        InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $')
    ])
    buttons.append([
        InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')
    ])
    return InlineKeyboardMarkup(buttons)

# Register handlers dynamically
for cmd, data in COMMANDS.items():
    dispatcher.add_handler(CommandHandler(cmd, data["handler"]))

dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# Scheduler jobs config
SCHEDULED_JOBS = [
    {"func": lambda: send_daily_report(dispatcher.bot), "trigger": "cron", "hour": 9, "minute": 0, "timezone": "Asia/Bangkok"},
    {"func": lambda: run_stealth_radar(dispatcher.bot), "trigger": "interval", "minutes": 5},
    {"func": lambda: check_price_targets(dispatcher.bot), "trigger": "interval", "minutes": 10},
    {"func": lambda: monitor_wallets(dispatcher.bot), "trigger": "interval", "minutes": 5},
    {"func": lambda: botnet_alerts(dispatcher.bot), "trigger": "interval", "minutes": 10}
]

def send_daily_report(bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)

def run_stealth_radar(bot):
    new_tokens = fetch_new_tokens()
    suspicious_tokens = filter_suspicious(new_tokens)
    chat_id = os.getenv("CHAT_ID")
    for token in suspicious_tokens:
        msg = (
            f"🚨 Suspicious new token detected!\n"
            f"Name: {token['name']}\n"
            f"Liquidity: ${token['liquidity']}\n"
            f"Social Signals: {token['socialSignals']}\n"
            f"Launch Time: {token['launchTime']}"
        )
        bot.send_message(chat_id=chat_id, text=msg)

scheduler = BackgroundScheduler()
for job in SCHEDULED_JOBS:
    scheduler.add_job(job["func"], job["trigger"], **{k: v for k, v in job.items() if k not in ["func", "trigger"]})
scheduler.start()

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
    updater.bot.set_my_commands([BotCommand(cmd, data["desc"]) for cmd, data in COMMANDS.items()])
    app.run(host='0.0.0.0', port=PORT)
