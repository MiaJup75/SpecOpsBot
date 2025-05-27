import os
import datetime
import requests
from db import get_tokens
from cost_tracker import get_dynamic_avg_cost
from telegram import Bot
from token_config import get_token_config

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")  # Make sure to set this env variable

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

def check_pnl(bot: Bot):
    tracked = get_tokens()
    lines = ["<b>📊 Multi-Token PnL Summary</b>\n"]
    any_data = False

    for symbol in tracked:
        symbol = symbol.upper()
        config = get_token_config(symbol)
        if not config:
            continue

        pair = config.get("pair")
        mint = config.get("mint")
        target = config.get("target_price", 0.0)

        if not mint or not pair:
            continue

        balance = get_token_balance(mint)
        if balance == 0:
            continue

        try:
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
            r = requests.get(url, timeout=5)
            info = r.json().get("pair", {})
            price = float(info.get("priceUsd", 0))

            avg_cost = get_dynamic_avg_cost(symbol) or 0.0
            if avg_cost == 0.0:
                continue

            est = price * balance
            pnl_pct = ((price - avg_cost) / avg_cost) * 100
            status = "🎯" if price >= target else ""

            lines.append(f"""<b>${symbol}</b> – {pnl_pct:+.1f}% {status}  
Est: ${est:,.0f} | P: ${price:.6f}\n""")
            any_data = True

        except Exception as e:
            print(f"[PnL fetch error for {symbol}] {e}")

    if not any_data:
        return "No PnL data available."

    lines.append(f"<i>Checked at {datetime.datetime.now().strftime('%H:%M:%S')}</i>")
    msg = "\n".join(lines)
    bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")
