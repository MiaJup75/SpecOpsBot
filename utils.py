import requests

def fetch_max_token_stats(token_address):
    url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={token_address}&time_frame=24h"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("data", {})
    return {}

def detect_suspicious_activity(stats):
    suspicious_flags = []
    if stats.get("price_change_pct") and abs(stats["price_change_pct"]) > 0.5:
        suspicious_flags.append("⚠️ Large price swing detected")
    if stats.get("volume_change_pct") and abs(stats["volume_change_pct"]) > 1.0:
        suspicious_flags.append("⚠️ Volume spike")
    return suspicious_flags