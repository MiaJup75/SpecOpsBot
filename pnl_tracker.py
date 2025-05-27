import os
import datetime
import requests
from db import get_tokens
from cost_tracker import get_dynamic_avg_cost

WALLET_ADDRESS = "FWg4kXnm3BmgrymEFo7BTE6iwEqgzdy4owo4qzx8WBjH"

# Add per-token config for pair/mint/target. avg_cost is now optional
TOKEN_OVERRIDES = {
    "MAX": {
        "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
        "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
        "target": 0.000050
    }
    # Add more tokens here with their pair + mint address
}

def get_token_balance(mint_address):
    url = f"https://public-api.solscan.io/account/tokens?account={WALLET_ADDRESS}"
    try:
        res = requests.get(url, timeout=10)
        for token in res.json():
            if token["tokenAddress"] == mint_address:
                return float(token["tokenAmount"]["uiAmountString"])
    except Exception as e:
        print(f"[Solscan Error] {e}")
    return 0.0

def fetch_pnl_data():
    symbol = "MAX"
    data = TOKEN_OVERRIDES.get(symbol)
    if not data:
        return None

    balance = get_token_balance(data['mint'])
    if balance == 0:
        return None

    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{data['pair']}"
        r = requests.get(url, timeout=5)
        info = r.json().get("pair", {})

        price = float(info.get("priceUsd", 0))
        avg_cost = get_dynamic_avg_cost() or 0.0
        if avg_cost == 0.0:
            return None

        pnl_pct = ((price - avg_cost) / avg_cost) * 100
        est_value = price * balance

        return {
            "holdings": balance,
            "avg_cost": avg_cost,
            "current_price": price,
            "pnl_pct": pnl_pct,
            "target_exit": 500000,  # example target exit market cap
            "sell_plan": {"amount": 2000000, "price": 0.00005},
            "estimated_value": est_value
        }
    except Exception as e:
        print(f"[PnL fetch error for {symbol}] {e}")
        return None

def check_max_pnl(bot):
    data = fetch_pnl_data()
    if not data:
        return

    lines = [f"""<b>📊 MAX Token PnL Summary</b>

• Holdings: {data['holdings']:.2f} MAX  
• Average Buy: {data['avg_cost']:.6f}  
• Current Price: {data['current_price']:.6f}  
• Unrealized PnL: {data['pnl_pct']:+.1f}%  
• Target Exit: ${data['target_exit']:,} Market Cap  
• Sell Plan: {data['sell_plan']['amount']:,} tokens @ {data['sell_plan']['price']:.6f}

<i>Checked at {datetime.datetime.now().strftime('%H:%M:%S')}</i>
"""]

    msg = "\n".join(lines)
    bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")
