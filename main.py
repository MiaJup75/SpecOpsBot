import logging
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from utils import (
    fetch_max_token_data,
    fetch_trending_tokens,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    track_position,
    send_target_alerts,
    get_meme_sentiment,
    detect_stealth_launches
)
from config import config
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config['telegram_token']
app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to SolMadSpecBot!\n"
        "Here's what I can do:\n\n"
        "• /max – MAX token stats\n"
        "• /trending – Top 5 Sol meme coins\n"
        "• /new – New token launches\n"
        "• /alerts – Suspicious activity\n"
        "• /wallets – Watchlist summaries\n"
        "• /pnl – PnL & break-even\n"
        "• /targetalerts – Price trigger zones\n"
        "• /sentiment – Meme coin mood check\n"
        "• /stealthlaunches – Low-social risky tokens\n\n"
        "📌 Type /help to view commands!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Available Commands:</b>\n"
        "/max – MAX token update\n"
        "/trending – Top 5 Sol meme coins\n"
        "/new – New token launches\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Tracked wallet activity\n"
        "/pnl – PnL and breakeven\n"
        "/targetalerts – Triggered price zones\n"
        "/sentiment – Meme sentiment index\n"
        "/stealthlaunches – Flagged risky tokens",
        parse_mode='HTML'
    )

async def max_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_max_token_data(update, context)

async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_trending_tokens(update, context)

async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_new_tokens(update, context)

async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_suspicious_activity(update, context)

async def wallets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await summarize_wallet_activity(update, context)

async def pnl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await track_position(update, context)

async def targetalerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_target_alerts(update, context)

async def sentiment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_meme_sentiment(update, context)

async def stealthlaunches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await detect_stealth_launches(update, context)

def main():
    logging.info("Running SolMadSpecBot...")
    app_builder = ApplicationBuilder().token(TOKEN).build()

    handlers = [
        (start, "start"),
        (help_command, "help"),
        (max_command, "max"),
        (trending_command, "trending"),
        (new_command, "new"),
        (alerts_command, "alerts"),
        (wallets_command, "wallets"),
        (pnl_command, "pnl"),
        (targetalerts_command, "targetalerts"),
        (sentiment_command, "sentiment"),
        (stealthlaunches_command, "stealthlaunches"),
    ]

    for handler_func, command_name in handlers:
        app_builder.add_handler(CommandHandler(command_name, handler_func))

    # Register autocomplete commands
    app_builder.bot.set_my_commands([
        BotCommand("start", "Start the bot and show help"),
        BotCommand("help", "Show command list"),
        BotCommand("max", "MAX token update"),
        BotCommand("trending", "Top 5 Sol meme coins"),
        BotCommand("new", "New token launches"),
        BotCommand("alerts", "Suspicious activity"),
        BotCommand("wallets", "Tracked wallet activity"),
        BotCommand("pnl", "PnL and breakeven"),
        BotCommand("targetalerts", "Price trigger alerts"),
        BotCommand("sentiment", "Meme sentiment score"),
        BotCommand("stealthlaunches", "Stealth tokens to avoid")
    ])

    # Scheduler (uses pytz only)
    scheduler = BackgroundScheduler(timezone="Asia/Bangkok")
    scheduler.add_job(lambda: fetch_max_token_data(None, None), "cron", hour=9)
    scheduler.start()

    app_builder.run_polling()

if __name__ == "__main__":
    main()
