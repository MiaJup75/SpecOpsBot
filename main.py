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
        [InlineKeyboardButton("🔍 Meme Sentiment Score", callback_data='sentiment'),
         InlineKeyboardButton("🤖 AI Trade", callback_data='tradeprompt')],
        [InlineKeyboardButton("📦 Meme Classification", callback_data='classify'),
         InlineKeyboardButton("🐞 Debug", callback_data='debug')],
        [InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
         InlineKeyboardButton("➖ Remove Wallet", switch_inline_query_current_chat='/removewallet ')],
        [InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $'),
         InlineKeyboardButton("❌ Remove Token", switch_inline_query_current_chat='/removetoken $')],
        [InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')],
        [InlineKeyboardButton("🤖 Auto Buy", switch_inline_query_current_chat='/autobuy $')],
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
/removewallet &lt;label&gt; /removetoken $TOKEN  
/autobuy $TOKEN [amount]

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
        'start': lambda: "Use the buttons or commands to interact with the bot.",
        'help': lambda: HELP_TEXT,
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
        'panel': lambda: "Use the panel buttons or commands to navigate."
    }

    response = func_map.get(command, lambda: "Unknown command")()
    query.edit_message_text(text=response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

def watch_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) < 1:
            update.message.reply_text("Usage: /watch <nickname> <wallet_address>\nExample: /watch MyWallet 4FEj7...", parse_mode=ParseMode.HTML)
            return
        if len(context.args) == 1:
            # No nickname provided, use address as label
            label = context.args[0][:8]
            address = context.args[0]
        else:
            label = context.args[0]
            address = context.args[1]
        add_wallet(label, address)
        update.message.reply_text(f"✅ Watching wallet:\n<b>{html.escape(label)}</b>\n<code>{address}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error in watch_command: {e}")
        update.message.reply_text("⚠️ Error adding wallet.")

def removewallet_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) < 1:
            update.message.reply_text("Usage: /removewallet <nickname>", parse_mode=ParseMode.HTML)
            return
        label = context.args[0]
        remove_wallet(label)
        update.message.reply_text(f"❌ Removed wallet with label: {html.escape(label)}", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error in removewallet_command: {e}")
        update.message.reply_text("⚠️ Error removing wallet.")

def wallets_command(update: Update, context: CallbackContext) -> None:
    wallets = get_wallets()
    if not wallets:
        update.message.reply_text("No wallets currently tracked.")
        return
    msg_lines = ["<b>👛 Watched Wallets</b>"]
    for label, addr in wallets:
        msg_lines.append(f"• <b>{html.escape(label)}</b>\n<code>{addr}</code>")
    update.message.reply_text("\n".join(msg_lines), parse_mode=ParseMode.HTML)

def addtoken_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /addtoken $TOKEN", parse_mode=ParseMode.HTML)
            return
        symbol = context.args[0].lstrip("$").upper()
        add_token(symbol)
        update.message.reply_text(f"✅ Watching token: ${symbol}", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error in addtoken_command: {e}")
        update.message.reply_text("⚠️ Error adding token.")

def removetoken_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /removetoken $TOKEN", parse_mode=ParseMode.HTML)
            return
        symbol = context.args[0].lstrip("$").upper()
        remove_token(symbol)
        update.message.reply_text(f"❌ Removed token: ${symbol}", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error in removetoken_command: {e}")
        update.message.reply_text("⚠️ Error removing token.")

def tokens_command(update: Update, context: CallbackContext) -> None:
    tokens = get_tokens()
    if not tokens:
        update.message.reply_text("No tokens being watched.")
        return
    token_list = "\n".join([f"• ${t}" for t in tokens])
    update.message.reply_text(f"<b>📋 Watched Tokens</b>\n{token_list}", parse_mode=ParseMode.HTML)

def autobuy_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text("Usage: /autobuy $TOKEN [amount]", parse_mode=ParseMode.HTML)
        return
    token = context.args[0].lstrip("$").upper()
    amount = float(context.args[1]) if len(context.args) > 1 else 0.1  # Default buy amount
    # Here you would invoke your wallet's autobuy functionality
    update.message.reply_text(f"🤖 Scheduled Auto Buy for ${token} with amount {amount}", parse_mode=ParseMode.HTML)

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
dispatcher.add_handler(CommandHandler("autobuy", autobuy_command))
dispatcher.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# --- Scheduler Job --- #
def send_daily_report(bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: send_daily_report(dispatcher.bot), 'cron', hour=9, minute=0, timezone='Asia/Bangkok')
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

# --- Run App --- #
if __name__ == '__main__':
    init_db()
    updater.bot.set_my_commands([
        BotCommand("start", "Show welcome message and buttons"),
        BotCommand("max", "Show MAX token stats"),
        BotCommand("wallets", "List all watched wallets"),
        BotCommand("watch", "Add a new wallet to watch"),
        BotCommand("removewallet", "Remove a wallet by nickname"),
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
        BotCommand("autobuy", "Auto-buy tokens with amount"),
        BotCommand("debug", "Run simulated debug outputs"),
        BotCommand("help", "Show help text")
    ])
    app.run(host='0.0.0.0', port=PORT)
