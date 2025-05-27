from telegram import Update, ParseMode, BotCommand
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    Dispatcher,
)
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from utils import (
    fetch_max_token_data,
    fetch_trending_tokens,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    track_position
)
from config import config

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

def is_allowed(user_id):
    return str(user_id) in WHITELIST

def start(update: Update, context: CallbackContext):
    welcome_message = (
        "<b>🤖 Welcome to SolMadSpecBot!</b>\n"
        "Here’s what I can do:\n\n"
        "/max – MAX token stats\n"
        "/trending – Top 5 Sol meme coins\n"
        "/new – New token launches\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Watchlist summaries\n"
        "/pnl – PnL & break-even"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_message,
        parse_mode=ParseMode.HTML
    )

def max_command(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    try:
        data = fetch_max_token_data()
        message = f"""
🐶 <b>MAX Token Update</b>
💰 Price: ${data['price']:,.8f}
🏛️ Market Cap: ${data['market_cap']:,.0f}
📉 Volume (24h): ${data['volume']:,.2f}
🏦 FDV: ${data['fdv']:,.0f}
📊 Buys: {data['buys']} | Sells: {data['sells']}
💧 Liquidity: ${data['liquidity']:,.2f}
📈 24H Change: {data['change']}%
🔢 Holders: {data.get('holders', 'N/A')}
🕐 Launch Time: {data['launch_time']}
🔗 <a href="{data['dex_url']}">View on Dexscreener</a>
"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Error fetching MAX data."
        )

def trending(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=fetch_trending_tokens(),
        parse_mode=ParseMode.HTML
    )

def new_tokens(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=fetch_new_tokens(),
        parse_mode=ParseMode.HTML
    )

def alerts(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=check_suspicious_activity(),
        parse_mode=ParseMode.HTML
    )

def wallets(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=summarize_wallet_activity(),
        parse_mode=ParseMode.HTML
    )

def pnl(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=track_position(),
        parse_mode=ParseMode.HTML
    )

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new_tokens))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("pnl", pnl))

# Telegram command autocomplete setup
updater.bot.set_my_commands([
    BotCommand("start", "Start the bot and show help"),
    BotCommand("max", "MAX token update"),
    BotCommand("trending", "Top 5 Sol meme coins"),
    BotCommand("new", "New token launches"),
    BotCommand("alerts", "Suspicious activity"),
    BotCommand("wallets", "Tracked wallet activity"),
    BotCommand("pnl", "PnL and breakeven"),
])

scheduler = BackgroundScheduler()
def send_daily_report():
    updater.bot.send_message(
        chat_id=WHITELIST[0],
        text="📊 Daily Report (placeholder)",
        parse_mode=ParseMode.HTML
    )

scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "OK"

if __name__ == "__main__":
    print("INFO: Running SolMadSpecBot...")
    app.run(host="0.0.0.0", port=10000)
