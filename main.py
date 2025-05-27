import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from flask import Flask, request
import os

from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens, remove_token
from wallet import Wallet
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

wallet = Wallet()

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 MAX", callback_data='max'),
         InlineKeyboardButton("👛 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("📈 Trending", callback_data='trending'),
         InlineKeyboardButton("🆕 New", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts'),
         InlineKeyboardButton("📊 PnL", callback_data='pnl')],
        [InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
         InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $')],
        [InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')]
    ])

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """<b>👋 Welcome to SolMadSpecBot!</b>

Use buttons or commands:
/max /wallets /trending  
/new /alerts /debug  
/pnl /sentiment /tradeprompt /classify  
/watch <wallet> [nickname] /addtoken $TOKEN /remove_token $TOKEN /tokens /autobuy $TOKEN AMOUNT /autobuy_trending

Daily updates at 9AM Bangkok time (GMT+7).""",
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
        'pnl': get_pnl_report
    }
    result = func_map.get(command, lambda: "Unknown command")()
    context.bot.send_message(chat_id=query.message.chat.id, text=result, parse_mode=ParseMode.HTML)

def watch_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) < 1:
            update.message.reply_text("Usage: /watch <wallet_address> [nickname]", parse_mode=ParseMode.HTML)
            return
        address = context.args[0]
        label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
        add_wallet(label, address)
        update.message.reply_text(f"✅ Watching wallet:\n<code>{address}</code> as \"{label}\"", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error in /watch: {e}")
        update.message.reply_text("⚠️ Error adding wallet.")

def wallets_command(update: Update, context: CallbackContext) -> None:
    wallets = get_wallets()
    if not wallets:
        update.message.reply_text("No wallets being tracked.")
        return
    msg = "<b>👛 Watched Wallets</b>\n" + "\n".join([f"• {label}\n<code>{addr}</code>" for label, addr in wallets])
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def addtoken_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /addtoken $TOKEN")
            return
        symbol = context.args[0].lstrip("$").upper()
        add_token(symbol)
        update.message.reply_text(f"✅ Watching token: ${symbol.upper()}")
    except Exception as e:
        logger.error(f"Error in /addtoken: {e}")
        update.message.reply_text("⚠️ Error adding token.")

def removetoken_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /remove_token $TOKEN")
            return
        symbol = context.args[0].lstrip("$").upper()
        remove_token(symbol)
        update.message.reply_text(f"✅ Removed token: ${symbol}")
    except Exception as e:
        logger.error(f"Error in /remove_token: {e}")
        update.message.reply_text("⚠️ Error removing token.")

def tokens_command(update: Update, context: CallbackContext) -> None:
    tokens = get_tokens()
    if not tokens:
        update.message.reply_text("No tokens being watched.")
        return
    token_list = "\n".join([f"• ${t}" for t in tokens])
    update.message.reply_text(f"<b>📋 Watched Tokens</b>\n{token_list}", parse_mode=ParseMode.HTML)

def autobuy_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 2:
            update.message.reply_text("Usage: /autobuy $TOKEN AMOUNT")
            return

        symbol = context.args[0].lstrip("$").upper()
        amount = float(context.args[1])

        tokens = get_tokens()
        if symbol not in tokens:
            update.message.reply_text(f"⚠️ Token ${symbol} is not in the watchlist. Add it using /addtoken.")
            return

        result = wallet.buy_token(symbol, amount)
        update.message.reply_text(result)
    except Exception as e:
        logger.error(f"Error in /autobuy: {e}")
        update.message.reply_text(f"⚠️ Error executing /autobuy: {e}")

def autobuy_trending_command(update: Update, context: CallbackContext) -> None:
    try:
        amount = 0.1  # default amount in SOL

        trending_text = get_trending_coins()
        first_line = trending_text.splitlines()[2]  # third line with first coin
        symbol = first_line.split("–")[0].strip().upper()

        tokens = get_tokens()
        if symbol not in tokens:
            update.message.reply_text(f"⚠️ Token ${symbol} is not in the watchlist. Add it using /addtoken.")
            return

        result = wallet.buy_token(symbol, amount)
        update.message.reply_text(f"Buying trending token ${symbol} for {amount} SOL.\n{result}")
    except Exception as e:
        logger.error(f"Error in /autobuy_trending: {e}")
        update.message.reply_text(f"⚠️ Error executing /autobuy_trending: {e}")

def debug_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(simulate_debug_output(), parse_mode=ParseMode.HTML)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("panel", panel_command))
dispatcher.add_handler(CommandHandler("max", lambda u, c: u.message.reply_text(get_max_token_stats(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("watch", watch_command))
dispatcher.add_handler(CommandHandler("addtoken", addtoken_command))
dispatcher.add_handler(CommandHandler("remove_token", removetoken_command))
dispatcher.add_handler(CommandHandler("tokens", tokens_command))
dispatcher.add_handler(CommandHandler("trending", lambda u, c: u.message.reply_text(get_trending_coins(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("new", lambda u, c: u.message.reply_text(get_new_tokens(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("alerts", lambda u, c: u.message.reply_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("debug", debug_command))
dispatcher.add_handler(CommandHandler("pnl", lambda u, c: u.message.reply_text(get_pnl_report(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("sentiment", lambda u, c: u.message.reply_text(get_sentiment_scores(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("tradeprompt", lambda u, c: u.message.reply_text(get_trade_prompt(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("classify", lambda u, c: u.message.reply_text(get_narrative_classification(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("autobuy", autobuy_command))
dispatcher.add_handler(CommandHandler("autobuy_trending", autobuy_trending_command))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

def send_daily_report(bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: send_daily_report(dispatcher.bot), 'cron', hour=9, minute=0, timezone='Asia/Bangkok')
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
    updater.bot.set_my_commands([
        BotCommand("start", "Show welcome message and buttons"),
        BotCommand("max", "Show MAX token stats"),
        BotCommand("wallets", "List all watched wallets"),
        BotCommand("watch", "Add a new wallet to watch"),
        BotCommand("addtoken", "Add a token to watch"),
        BotCommand("remove_token", "Remove a token from watchlist"),
        BotCommand("tokens", "List all tracked tokens"),
        BotCommand("trending", "View top trending meme coins"),
        BotCommand("new", "Show new token launches"),
        BotCommand("alerts", "Show whale/dev/suspicious alerts"),
        BotCommand("pnl", "Check your MAX token PnL"),
        BotCommand("sentiment", "See meme sentiment scores"),
        BotCommand("tradeprompt", "AI-generated trade idea"),
        BotCommand("classify", "Classify token narratives"),
        BotCommand("autobuy", "Buy tokens automatically"),
        BotCommand("autobuy_trending", "Buy the top trending meme coin"),
        BotCommand("debug", "Run simulated debug outputs"),
        BotCommand("help", "Show this help message")
    ])
    app.run(host='0.0.0.0', port=PORT)
