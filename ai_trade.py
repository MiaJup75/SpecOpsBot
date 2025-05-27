import os
import requests
import random
import datetime

def get_ai_trade_prompt(bot):
    try:
        # Sample token pool (in practice this would be dynamically ranked)
        tokens = [
            {"symbol": "MAX", "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc", "theme": "dog/meme"},
            {"symbol": "ZAZA", "pair": "fakezazazazazaza111", "theme": "dubai/luxury"},
            {"symbol": "CHAD", "pair": "fakeswaggpair", "theme": "gym/hustle"}
        ]

        pick = random.choice(tokens)
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pick['pair']}"
        res = requests.get(url, timeout=5)
        data = res.json().get("pair", {})

        price = float(data.get("priceUsd", 0))
        buys = data.get("txns", {}).get("h1", {}).get("buys", 0)
        sells = data.get("txns", {}).get("h1", {}).get("sells", 0)
        lp = float(data.get("liquidity", {}).get("usd", 0))
        volume = float(data.get("volume", {}).get("h1", 0))
        change = float(data.get("priceChange", {}).get("h1", 0))

        risk = "High" if sells > buys * 2 else "Medium" if sells > buys else "Low"

        msg = f"""<b>📈 AI Trade Prompt</b>

🪙 <b>Token:</b> ${pick['symbol']}  
📊 <b>Price:</b> ${price:.6f}  
💧 <b>Liquidity:</b> ${lp:,.0f}  
🔁 <b>Vol (1h):</b> ${volume:,.0f}  
🧠 <b>Sentiment:</b> {pick['theme']}  
📉 <b>Buys/Sells:</b> {buys} / {sells}  
⚠️ <b>Risk Level:</b> {risk}

<i>Prompt generated: {datetime.datetime.now().strftime('%H:%M:%S')}</i>  
🔗 <a href="https://dexscreener.com/solana/{pick['pair']}">View on Dexscreener</a>
"""
        bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")

    except Exception as e:
        print(f"[AI Trade Prompt Error] {e}")
