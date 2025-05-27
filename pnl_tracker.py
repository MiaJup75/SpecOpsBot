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

def check_max_pnl(bot):
    tracked = get_tokens()
    lines = ["<b>📊 Multi-Token PnL Summary</b>\n"]
    any_data = False

    for symbol in tracked:
        symbol = symbol.upper()
        data = TOKEN_OVERRIDES.get(symbol)
        if not data:
            continue

        pair = data.get("pair")
        mint = data.get("mint")
        target = data.get("target", 0.0)

        balance = get_token_balance(mint)
        if balance == 0:
            continue

        # Fetch price data
        try:
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
            r = requests.get(url, timeout=5)
            info = r.json().get("pair", {})
            price = float(info.get("priceUsd", 0))
            mcap = float(info.get("marketCap", 0))
            lp = float(info.get("liquidity", {}).get("usd", 0))
            vol = float(info.get("volume", {}).get("h24", 0))

            # Dynamic average cost
            avg_cost = get_dynamic_avg_cost() or 0.0
            if avg_cost == 0.0:
                continue

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
