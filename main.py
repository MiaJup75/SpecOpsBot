
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    is_allowed
)
from config import config

app = Flask(__name__)
TOKEN = config["telegram_token"]
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return "Bot is live!"

@app.route('/hook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

def start(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text="🤖 Welcome to SolMadSpecBot! Use /max, /trending, /wallets, /new, /alerts")

def max_token(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    data = fetch_max_token_data()
    message = (
        f"🐶 <b>MAX Token Update</b>\n"
        f"💰 Price: ${data['price']}\n"
        f"🏛️ Market Cap: ${data['market_cap']:,}\n"
        f"📉 Volume (24h): ${data['volume']:,}\n"
        f"🏦 FDV: ${data['fdv']:,}\n"
        f"📊 Buys: {data['buys']} | Sells: {data['sells']}\n"
        f"💧 Liquidity: ${data['liquidity']:,}\n"
        f"📈 24H Change: {data['price_change']}%\n"
        f"🔢 Holders: {data['holders']}\n"
        f"🕐 Launch Time: {data['launched_at']}\n"
        f"🔗 <a href='https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc'>View on Dexscreener</a>"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')

def trending(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = get_trending_coins()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')

def send_daily_report():
    for uid in config["whitelist"]:
        bot.send_message(chat_id=uid, text="📊 Daily Report (placeholder)", parse_mode='HTML')

def setup_handlers():
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("max", max_token))
    dispatcher.add_handler(CommandHandler("trending", trending))

if __name__ == "__main__":
    logger.info("Running SolMadSpecBot...")
    bot.set_webhook(url="https://solmad-spec-bot.onrender.com/hook")
    setup_handlers()
    scheduler = BackgroundScheduler(timezone="Asia/Bangkok")
    scheduler.add_job(send_daily_report, "cron", hour=9)
    scheduler.start()
    app.run(host="0.0.0.0", port=10000)
