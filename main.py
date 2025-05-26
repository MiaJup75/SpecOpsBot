
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher, Updater
import logging

TOKEN = "YOUR_TOKEN"

bot = Bot(token=TOKEN)
updater = Updater(bot=bot, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

def start(update: Update, context):
    welcome_message = f"""<b>Welcome to SolMadSpecBot!</b>
Here are your available commands:
/max – Get MAX token update
/wallets – Monitor wallet activity
/trending – Top trending Solana meme coins
/new – New tokens under 12h old
/alerts – Suspicious activity flags
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message, parse_mode="HTML")

dispatcher.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    print("Bot is starting...")
    updater.start_polling()
    updater.idle()
