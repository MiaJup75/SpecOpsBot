import os
import requests
import datetime
from telegram import Bot

# Store tokens we've alerted on in-memory or persist as needed
alerted_tokens = set()

MIN_LP_USD = 10000
MAX_TOKEN_AGE_MIN = 30

def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/tokens/solana"
    try:
        response = requests.get(url, timeout=10).json()
        tokens = response.get("tokens", [])
        recent_tokens = []
        cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=MAX_TOKEN_AGE_MIN)

        for token in tokens:
            launch_ts = token.get("launchTime") or token.get("createdAt") or 0
            if launch_ts:
                launch_dt = datetime.datetime.utcfromtimestamp(launch_ts)
                if launch_dt > cutoff_time:
                    recent_tokens.append(token)
        return recent_tokens
    except Exception as e:
        print(f"[stealth_launch] Error fetching new tokens: {e}")
        return []

def filter_tokens_by_lp(tokens, min_lp_usd=MIN_LP_USD):
    filtered = []
    for token in tokens:
        lp_usd = token.get("liquidityUSD") or 0
        if lp_usd >= min_lp_usd:
            filtered.append(token)
    return filtered

def check_contract_safety(token_address):
    # Placeholder for actual contract inspection logic
    # For example, fetch contract code, check for suspicious functions like 'setFee', 'transferFrom' backdoors, honeypots
    # Return False if suspicious, True if safe
    # For MVP, just return True
    return True

def check_social_signals(token_symbol):
    # Placeholder for social media checks (Telegram/X/Discord)
    # You can later integrate API calls or scrapers here
    # For MVP, assume no social activity
    return 0  # Number of mentions or score

def scan_new_tokens(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    new_tokens = fetch_new_tokens()
    filtered_tokens = filter_tokens_by_lp(new_tokens)

    if not filtered_tokens:
        return

    for token in filtered_tokens:
        token_id = token.get("id") or token.get("tokenAddress") or token.get("address") or token.get("name")

        # Skip already alerted tokens
        if token_id in alerted_tokens:
            continue

        # Honeypot/contract safety check
        if not check_contract_safety(token_id):
            print(f"[stealth_launch] Skipping suspicious token {token.get('name')}")
            continue

        # Social signal check
        social_score = check_social_signals(token.get("symbol", ""))

        # Only alert if social score below threshold (e.g., very low buzz tokens)
        if social_score > 5:
            print(f"[stealth_launch] Token {token.get('symbol')} has high social signals ({social_score}), skipping alert")
            continue

        # Construct alert message
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "???")
        lp_usd = token.get("liquidityUSD", 0)
        launch_time = token.get("launchTime", 0)
        launch_dt = datetime.datetime.utcfromtimestamp(launch_time).strftime('%Y-%m-%d %H:%M:%S') if launch_time else "Unknown"

        msg = (f"🚀 <b>New Stealth Token Launch Detected!</b>\n"
               f"Name: {name} (${symbol})\n"
               f"Liquidity: ${lp_usd:,.0f}\n"
               f"Launch Time (UTC): {launch_dt}\n"
               f"Social Mentions: {social_score}\n"
               f"Check it out on Dexscreener!")

        try:
            bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")
            alerted_tokens.add(token_id)
        except Exception as e:
            print(f"[stealth_launch] Failed to send Telegram message: {e}")
