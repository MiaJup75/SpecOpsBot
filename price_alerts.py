import os
import requests
import datetime
import sqlite3

# Define tracked tokens and thresholds
WATCHED_TOKENS = [
    {"symbol": "MAX", "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc", "target_price": 0.000050},
    {"symbol": "ZAZA", "pair": "fakezazazazazaza111", "target_price": 0.001000}
]

def init_alert_db():
    conn = sqlite3.connect("price_alerts.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS triggered (pair TEXT PRIMARY KEY, ts TEXT)")
    conn.commit()
    conn.close()

def is_triggered(pair):
    conn = sqlite3.connect("price_alerts.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM triggered WHERE pair = ?", (pair,))
    hit = c.fetchone()
    conn.close()
    return hit is not None

def mark_triggered(pair):
    conn = sqlite3.connect("price_alerts.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO triggered (pair, ts) VALUES (?, ?)", (pair, str(datetime.datetime.now())))
    conn.commit()
    conn.close()

def check_price_triggers(bot):
    try:
        init_alert_db()
        for token in WATCHED_TOKENS:
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token['pair']}"
            r = requests.get(url, timeout=5)
            data = r.json().get("pair", {})

            price = float(data.get("priceUsd", 0))
            if price >= token["target_price"] and not is_triggered(token["pair"]):
                msg = f"""<b>🎯 Price Target Hit</b>

Token: ${token["symbol"]}  
Current Price: ${price:.6f}  
Target: ${token["target_price"]:.6f}

🔗 <a href="https://dexscreener.com/solana/{token['pair']}">View on Dexscreener</a>
"""
                bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")
                mark_triggered(token["pair"])

    except Exception as e:
        print(f"[Price Alert Error] {e}")
