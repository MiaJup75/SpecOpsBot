import os
import datetime
import requests

# MAX config (could be adapted to any token in future)
MAX_TOKEN = {
    "symbol": "MAX",
    "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
    "avg_cost": 0.000028,
    "holdings": 10_450_000,
    "target_price": 0.000050,
}

def check_max_pnl(bot):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{MAX_TOKEN['pair']}"
        res = requests.get(url, timeout=5)
        data = res.json().get("pair", {})

        price = float(data.get("priceUsd", 0))
        cost = MAX_TOKEN["avg_cost"]
        held = MAX_TOKEN["holdings"]
        mcap = float(data.get("marketCap", 0))
        lp = float(data.get("liquidity", {}).get("usd", 0))
        volume = float(data.get("volume", {}).get("h24", 0))

        pnl_pct = ((price - cost) / cost) * 100
        est_value = price * held
        target_hit = price >= MAX_TOKEN["target_price"]

        text = f"""<b>📊 MAX Token PnL Tracker</b>

💰 <b>Holdings:</b> {held:,.0f} MAX  
📉 <b>Avg Cost:</b> ${cost:.6f}  
📈 <b>Current Price:</b> ${price:.6f}  
🧮 <b>PnL:</b> {pnl_pct:+.2f}%  
💼 <b>Est. Value:</b> ${est_value:,.2f}

🏷 <b>Market Cap:</b> ${mcap:,.0f}  
💧 <b>Liquidity:</b> ${lp:,.0f}  
🔁 <b>Volume:</b> ${volume:,.0f}

<i>Checked at {datetime.datetime.now().strftime('%H:%M:%S')}</i>
"""

        if target_hit:
            text += f"\n\n🎯 <b>Target Reached:</b> ${price:.6f} ≥ ${MAX_TOKEN['target_price']:.6f}\n<b>Suggested Action:</b> Sell 2M MAX"

        bot.send_message(chat_id=os.getenv("CHAT_ID"), text=text, parse_mode="HTML")

    except Exception as e:
        print(f"[PnL Tracker Error] {e}")
