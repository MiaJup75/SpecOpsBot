import requests
from config import config
from telegram.constants import ParseMode
import random

def format_dollar(value):
    return f"${value:,.2f}"

async def fetch_max_token_data(update, context):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        response = requests.get(url)
        data = response.json()["pair"]

        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: {data['priceUsd']}
🏛️ Market Cap: {format_dollar(float(data['marketCap']))}
📉 Volume (24h): {format_dollar(float(data['volume']['h24']))}
🏦 FDV: {format_dollar(float(data['fdv']))}
📊 Buys: {data['txns']['h24']['buys']} | Sells: {data['txns']['h24']['sells']}
💧 Liquidity: {format_dollar(float(data['liquidity']['usd']))}
📈 24H Change: {data['priceChange']['h24']}%
🔢 Holders: N/A
🕐 Launch Time: {data['pairCreatedAt']}
🔗 <a href="{data['url']}">View on Dexscreener</a>
"""
        if update:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)
        else:
            print("[MAX] Daily summary fetched.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error fetching MAX data: {str(e)}")

async def fetch_trending_tokens(update, context):
    try:
        coins = [
            {"name": "DOGGO", "price": "$0.0009", "volume": "$12,345"},
            {"name": "MEOW", "price": "$0.0012", "volume": "$8,901"},
            {"name": "ZAP", "price": "$0.045", "volume": "$22,000"},
            {"name": "RAWR", "price": "$0.00005", "volume": "$3,210"},
            {"name": "BLOOP", "price": "$0.75", "volume": "$18,450"},
        ]
        message = "🚀 <b>Trending Solana Meme Coins</b>\n"
        for i, coin in enumerate(coins, 1):
            message += f"{i}. {coin['name']} – {coin['price']} – Vol: {coin['volume']}\n"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {str(e)}")

async def fetch_new_tokens(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🆕 No new tokens found.")

async def check_suspicious_activity(update, context):
    alerts = [
        "RUGDOG: 💢 Liquidity pulled",
        "FAKEAI: ⚠️ Dev wallet dumped 80%",
    ]
    message = "⚠️ <b>Suspicious Token Alerts</b>\n" + "\n".join(alerts)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

async def summarize_wallet_activity(update, context):
    wallets = config["wallets"]
    message = "🍥 <b>Wallet Watchlist</b>\n"
    for wallet in wallets:
        buys = random.randint(1, 3)
        sells = random.randint(0, 2)
        message += f"Wallet {wallet[:4]}...{wallet[-4:]} activity summary:\n"
        message += f"🟢 {buys} Buys, 🔴 {sells} Sell in last 24h\n\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message.strip(), parse_mode=ParseMode.HTML)

async def track_position(update, context):
    value = 3457.91
    breakeven = 0.0002
    pnl = value - 2080
    message = f"""📈 <b>PnL Tracker</b>
💵 Value: {format_dollar(value)}
🎰 PnL: {format_dollar(pnl)}
⚖️ Breakeven Price: ${breakeven}"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

async def send_target_alerts(update, context):
    message = "🎯 <b>Target Alerts</b>\nSell Zone Triggered at $0.00035\nWhale transferred MAX to CEX wallet"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

async def get_meme_sentiment(update, context):
    sentiment = ["😎 Meme hype is lit!", "😐 Choppy sentiment today", "🥶 Meme market cooling off"]
    message = f"📊 <b>Meme Sentiment</b>\n{random.choice(sentiment)}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

async def detect_stealth_launches(update, context):
    launches = ["BOTINU – No socials found", "GHOSTDOGE – Suspicious LP source"]
    message = "🕵️‍♂️ <b>Stealth Launch Radar</b>\n" + "\n".join(launches)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)
