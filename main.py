from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
from telegram.ext import MessageHandler, Filters
import json, time, threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import requests

# Load config
with open("config.json") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config.get("whitelist", [])
WALLETS = config["wallets"]
MAX_TOKEN = config["max_token"]
TZ = pytz.timezone("Asia/Bangkok")


# Telegram bot logic
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if WHITELIST and user_id not in WHITELIST:
        update.message.reply_text("🚫 You’re not authorized to use this bot.")
        return

    update.message.reply_text(
        "🤖 Welcome to SolMadSpecBot!\nTracking wallets, MAX token & meme coins daily..."
    )

    def max_command(update: Update, context: CallbackContext):
        url = "https://multichain-api.birdeye.so/solana/overview/token_stats?address=EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump&time_frame=24h"
        headers = {"X-API-KEY": "public"}

        try:
            print("Fetching MAX token price...")
            response = requests.get(url, headers=headers).json()
            data = response.get("data", {})
            price = float(data.get("price", 0))
            market_cap = float(data.get("market_cap", 0))
            price_change = float(data.get("price_change_24h", 0))
            volume = float(data.get("volume_24h", 0))
            fdv = float(data.get("fdv", 0))
            SWING_THRESHOLD = 10
            swing_emoji = ""
            if abs(price_change) >= SWING_THRESHOLD:
                swing_emoji = "🚨" if price_change < 0 else "🚀"
                if volume > 5000:
                    message += f"🚨 *Volume Spike!* ${volume:,.0f} traded in last 24h\n"
                
            message = (
                f"📊 *MAX Token Stats*\n"
                f"💰 Price: ${price:.6f}\n"
                f"📈 Market Cap: ${market_cap:,.0f}\n"
                f"📊 24h Volume: ${volume:,.0f}\n"
                f"🔄 24h Change: {price_change:+.2f}% {swing_emoji}\n"
                f"🧮 FDV: ${fdv:,.0f}\n"
                f"\n🔗 [View on Birdeye](https://birdeye.so/token/EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump?chain=solana)"
            )
    try:
        print("Fetching MAX token price...")
        response = requests.get(
            f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h",
            headers={"X-API-KEY": "public"}
        )
        data = response.json().get("data", {})
        print(data)

        price = float(data.get("price", 0))
        market_cap = round(price * 1_000_000_000, 2)

        message = f"🌐 MAX Token Info:\nPrice: ${price:.9f}\nMarket Cap: ${market_cap:,.2f}"
        update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        print("Error occurred:", e)
        message = f"⚠️ Error fetching MAX data: {e}"
        update.message.reply_text(message)
        
    def send_daily_report(context: CallbackContext):
    
        url = "https://multichain-api.birdeye.so/solana/overview/token_stats?address=EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump&time_frame=24h"
        headers = {"X-API-KEY": "public"}
        response = requests.get(url, headers=headers).json()
        data = response.get("data", {})

        price = float(data.get("price", 0))
        market_cap = int(data.get("market_cap", 0))
        price_change = float(data.get("price_change_24h", 0))
        volume = float(data.get("volume_24h", 0))
        fdv = float(data.get("fdv", 0))
        
        alert_emoji = ""
        if price_change >= 10:
            alert_emoji = "🚀"
        elif price_change <= -10:
            alert_emoji = "⚠️"

        
            
        message = (
            f"📊 *MAX Token Stats* {alert_emoji}\n"
            f"💰 Price: ${price:.6f}\n"
            f"📈 Market Cap: ${market_cap:,.0f}\n"
            f"📊 24h Change: {price_change:+.2f}%\n"
            f"🔄 24h Volume: ${volume:,.0f}\n"
            f"🏗️ FDV: ${fdv:,.0f}\n"
            f"\n🔗 [View on Birdeye](https://birdeye.so/token/EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump?chain=solana)"
        )

        if abs(price_change) > 10:
            message += "\n\n🚨 *High Price Volatility Alert!* 🚨"

        if volume > 5000:
            message += f"\n🔥 *Volume Spike Detected!* Over $5K in 24h volume!"

        for uid in WHITELIST:
    sent_msg = context.bot.send_message(chat_id=uid, text=message, parse_mode='Markdown')

    # Unpin any previously pinned messages (optional cleanup)
    try:
        context.bot.unpin_all_chat_messages(chat_id=uid)
    except:
        pass

    # Pin the new message without notification
    context.bot.pin_chat_message(chat_id=uid, message_id=sent_msg.message_id, disable_notification=True)
    except Exception as e:
        for uid in WHITELIST:
            context.bot.send_message(chat_id=uid, text="⚠️ Failed to send daily MAX update.")

def run_scheduler(updater: Updater):
    scheduler = BackgroundScheduler(timezone=TZ)
    scheduler.add_job(send_daily_report,
                      trigger='cron',
                      hour=9,
                      minute=0,
                      args=[updater.bot])
    scheduler.start()


def max_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        update.message.reply_text("⛔ You're not authorized to use this bot.")
        return
        
    print("🔧 /max command was triggered")
    print(f"User ID triggering /max: {user_id}")

    try:
        response = requests.get(
            f"https://public-api.birdeye.so/public/token/price?address={MAX_TOKEN}&chain=solana",
            headers={"x-api-key": "public"})
        data = response.json()
        print(data)
        price = float(data.get("data", {}).get("value", 0))
        market_cap = round(price * 1_000_000_000, 2)

        message = f"🪙 MAX Token Info:\nPrice: ${price:.9f}\nMarket Cap: ${market_cap:,.2f}"
    except Exception as e:
        message = f"⚠️ Error fetching MAX data: {e}"

    update.message.reply_text(message)

def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text("❓ Unknown command received.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("max", max_command))
    dp.add_handler(MessageHandler(Filters.command, unknown_command))

    run_scheduler(updater)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
