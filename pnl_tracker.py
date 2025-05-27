import os
import datetime
import requests
from db import get_tokens

WALLET_ADDRESS = "FWg4kXnm3BmgrymEFo7BTE6iwEqgzdy4owo4qzx8WBjH"

# Optional: set avg cost + target for each token (customize as needed)
TOKEN_OVERRIDES = {
    "MAX": {
        "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
        "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
        "avg_cost": 0.000028,
        "target": 0.000050
    },
    "ZAZA": {
        "pair": "fakezazazazazaza111",
        "mint": "ZAZAZAZA123456789abcdef",
        "avg_cost": 0.0015,
        "target": 0.0020
    }
    # Add more tokens if needed
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

def check_max_pnl(bot):
    tracked = get_tokens()
    lines = ["<b>📊 Multi-Token PnL Summary</b>\n"]
    any_data = False

    for symbol in tracked:
        data = TOKEN_OVERRIDES.get(symbol.upper())
        if not data:
            continue

        pair = data["pair"]
        mint = data["mint"]
        avg_cost = data.get("avg_cost", 0.0)
        target = data.get("target", 0.0)

        balance = get_token_balance(mint)
        if balance == 0:
            continue

        try:
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
            r = requests.get(url, timeout=5)
            info = r.json().get("pair", {})
            price = float(info.get("priceUsd", 0))
            mcap = float(info.get("marketCap", 0))
            lp = float(info.get("liquidity", {}).get("usd", 0))
            vol = float(info.get("volume", {}).get("h24", 0))

            est = price * balance
            pnl_pct = ((price - avg_cost) / avg_cost) * 100

            status = "🎯" if price >= target else ""
            lines.append(f"""<b>${symbol}</b> – {pnl_pct:+.1f}% {status}  
Est: ${est:,.0f} | P: ${price:.6f}  
MC: ${mcap:,.0f} | LP: ${lp:,.0f} | Vol: ${vol:,.0f}\n""")
            any_data = True

        except Exception as e:
            print(f"[PnL fetch error for {symbol}] {e}")

    if not any_data:
        return

    lines.append(f"<i>Checked at {datetime.datetime.now().strftime('%H:%M:%S')}</i>")
    msg = "\n".join(lines)
    bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")
