import datetime
import requests

def get_max_token_stats() -> str:
    try:
        pair_address = "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if 'pair' not in data:
            return "⚠️ MAX token data unavailable."

        p = data['pair']
        price = p['priceUsd']
        market_cap = p['fdv']
        volume = p['volume']['h24']
        liquidity = p['liquidity']['usd']
        last_updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return f"""<b>💰 MAX Token Stats</b>

Price: ${price}
Market Cap: ${int(market_cap):,}
24h Volume: ${int(volume):,}
Liquidity: ${int(liquidity):,}

<i>Last updated: {last_updated}</i>
"""
    except Exception as e:
        return "⚠️ Unable to fetch MAX token data."

# Leave other functions untouched — you already have:
# get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
# get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
# get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
