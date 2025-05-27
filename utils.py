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
        market_cap = float(p.get('marketCap', 0))
        volume = float(p['volume']['h24'])
        liquidity = float(p['liquidity']['usd'])
        buys = p['txns']['h24']['buys']
        sells = p['txns']['h24']['sells']
        change = float(p.get('priceChange', {}).get('h24', 0))
        fdv = float(p.get('fdv', 0))
        launch_ts = int(p.get('pairCreatedAt', 0))
        launch_date = datetime.datetime.fromtimestamp(launch_ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
        pair_name = p.get("baseToken", {}).get("symbol", "MAX")

        dex_link = f"https://dexscreener.com/solana/{pair_address}"

        return f"""<b>
