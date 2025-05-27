import requests
import datetime

def fetch_recent_gas_prices() -> str:
    try:
        # Example API: Replace with real Solana gas price API if available
        # This is a placeholder API endpoint — you might need to adjust based on real data sources
        url = "https://public-api.solscan.io/gas-fees/recent"
        response = requests.get(url, timeout=5)
        data = response.json()

        # Example processing — adapt based on actual API response structure
        avg_fee = data.get("averageFee", "N/A")
        max_fee = data.get("maxFee", "N/A")
        min_fee = data.get("minFee", "N/A")
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

        return f"""<b>⛽ Solana Gas Fees (Recent)</b>

Average Fee: {avg_fee} lamports  
Max Fee: {max_fee} lamports  
Min Fee: {min_fee} lamports

<i>Last updated: {timestamp}</i>
"""
    except Exception as e:
        return f"⚠️ Unable to fetch gas price data: {e}"
