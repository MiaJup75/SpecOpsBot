import logging
from flask import Flask, request
from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    fetch_new_tokens,
    check_suspicious_activity,
    track_position,
    summarize_wallet_activity,
    is_allowed
)
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config["telegram_token"])
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

app = Flask(__name__)
scheduler = BackgroundScheduler()

@app.route("/")
def index():
    return "SolMadSpecBot is running!"

@app.route(f"/hook", methods=["POST"])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

def start(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    welcome = (
        "<b>Welcome to SolMadSpecBot!</b>\n"
        "Here’s what I can do:\n\n"
        "/max – MAX token stats\n"
        "/trending – Top 5 Sol meme coins\n"
        "/new – New token launches\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Watchlist summaries\n"
        "/pnl – PnL & break-even\n"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome, parse_mode="HTML")

def max(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    data = fetch_max_token_data()
    if data:
        message = (
            f"🐶 <b>MAX Token Update</b>\n"
            f"💰 Price: ${data['price']}\n"
            f"🏛️ Market Cap: ${data['market_cap']}\n"
            f"📉 Volume (24h): ${data['volume']}\n"
            f"🏦 FDV: ${data['fdv']}"
        )
    else:
        message = "Failed to fetch MAX token data."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def trending(update, context):
    coins = get_trending_coins()
    if not coins:
        message = "No trending coins found."
    else:
        message = "<b>🚀 Trending Solana Meme Coins</b>\n"
        for i, coin in enumerate(coins, 1):
            name = coin['baseToken']['symbol']
            price = coin.get('priceUsd', '?')
            vol = coin.get('volume', {}).get('h24', '?')
            message += f"{i}. {name} – ${price} – Vol: ${vol}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def new(update, context):
    tokens = fetch_new_tokens()
    if not tokens:
        message = "No new tokens found."
    else:
        message = "<b>🆕 New Token Launches</b>\n"
        for token in tokens:
            name = token['baseToken']['symbol']
            price = token.get('priceUsd', '?')
            vol = token.get('volume', {}).get('h24', '?')
            timestamp = token.get("pairCreatedAt", 0)
            message += f"• {name} – ${price} – Vol: ${vol}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def alerts(update, context):
    flags = check_suspicious_activity()
    if not flags:
        message = "No suspicious activity detected."
    else:
        message = "<b>⚠️ Suspicious Token Alerts</b>\n"
        for item in flags:
            message += f"{item['token']}: {item['flag']}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def wallets(update, context):
    wallets = config["wallets"]
    message = "<b>👛 Wallet Watchlist</b>\n"
    for wallet in wallets:
        summary = summarize_wallet_activity(wallet)
        message += f"{summary}\n\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message.strip(), parse_mode="HTML")

def pnl(update, context):
    stats = track_position()
    if stats:
        message = (
            f"<b>📈 PnL Tracker</b>\n"
            f"💵 Value: ${stats['value']}\n"
            f"🧮 PnL: ${stats['pnl']}\n"
            f"⚖️ Breakeven Price: ${stats['breakeven']}"
        )
    else:
        message = "Could not calculate PnL."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def send_daily_report():
    try:
        for uid in config["whitelist"]:
            bot.send_message(chat_id=uid, text="📊 Daily Report (placeholder)", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("pnl", pnl))

# Set / command suggestions
bot.set_my_commands([
    BotCommand("start", "Start the bot and show help"),
    BotCommand("max", "MAX token update"),
    BotCommand("trending", "Top 5 Sol meme coins"),
    BotCommand("new", "New token launches"),
    BotCommand("alerts", "Suspicious activity"),
    BotCommand("wallets", "Tracked wallet activity"),
    BotCommand("pnl", "PnL and breakeven")
])

scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")
scheduler.start()

if __name__ == "__main__":
    logger.info("Running SolMadSpecBot...")
    app.run(host="0.0.0.0", port=10000)
