import os
import datetime
import requests
from db import get_tokens, get_wallets
from cost_tracker import get_dynamic_avg_cost

TOKEN_OVERRIDES = {
    "MAX": {
        "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
        "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
        "target": 0.000050
    }
}

def get_token_balance(wallet_address, mint_address):
    url = f"https://public-api.solscan.io/account/tokens?account={wallet_address}"
    try:
        res = requests.get(url, timeout=10)
        for token in res.json():
            if token["tokenAddress"] == mint_address:
                return float(token["tokenAmount"]["uiAmountString"])
    except Exception as e:
        print(f"[Solscan Error] {e}")
    return 0.0

def get_total_token_balance(mint_address):
    wallets = get_wallets()
    total_balance = 0.0
    for label, wallet_addr in wallets:
        bal = get_token_balance(wallet_addr, mint_address)
        total_balance += bal
    return total_balance

def get_pnl_report():
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

        balance = get_total_token_balance(mint)
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

            avg_cost = get_dynamic_avg_cost(symbol) or 0.0
            if avg_cost == 0.0:
                continue

            est = price * balance
            pnl_pct = ((price - avg_cost) / avg_cost) * 100
            status = "🎯" if price >= target else ""

            lines.append(f"""<b>${symbol}</b> – {pnl_pct:+.1f}% {status}  
Holdings: {balance:,.2f}  
Est: ${est:,.0f} | P: ${price:.6f}  
MC: ${mcap:,.0f} | LP: ${lp:,.0f} | Vol: ${vol:,.0f}\n""")
            any_data = True

        except Exception as e:
            print(f"[PnL fetch error for {symbol}] {e}")

    if not any_data:
        return "No PnL data available for your tracked tokens."

    lines.append(f"<i>Checked at {datetime.datetime.now().strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)
