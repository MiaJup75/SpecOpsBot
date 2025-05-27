import time
import requests
import os

SCANNED_TOKENS_FILE = "scanned_tokens.txt"

def load_scanned_tokens():
    try:
        with open(SCANNED_TOKENS_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

def save_scanned_token(token_address):
    with open(SCANNED_TOKENS_FILE, "a") as f:
        f.write(token_address + "\n")

def fetch_new_tokens():
    # Replace with actual API to fetch newly launched tokens (last ~30m)
    # Mock example returning list of token addresses
    return [
        "TokenAddress1",
        "TokenAddress2",
        "TokenAddress3"
    ]

def is_honeypot(token_address):
    # Placeholder honeypot check - call contract analysis APIs or simulate tx
    # Return True if honeypot detected, else False
    return False

def check_social_signals(token_address):
    # Placeholder for social signal analysis, e.g. low TG mentions, low volume
    # Return True if suspicious (low signals), False if healthy
    return True

def scan_new_tokens(bot):
    chat_id = os.getenv("CHAT_ID")
    scanned = load_scanned_tokens()
    new_tokens = fetch_new_tokens()

    for token in new_tokens:
        if token in scanned:
            continue  # skip already scanned tokens

        honeypot = is_honeypot(token)
        social_flag = check_social_signals(token)

        if honeypot:
            msg = f"🚨 Honeypot detected on new token: {token}"
            bot.send_message(chat_id=chat_id, text=msg)
        elif social_flag:
            msg = f"⚠️ Suspicious new token detected with low social signals: {token}"
            bot.send_message(chat_id=chat_id, text=msg)
        else:
            msg = f"✅ New token looks safe: {token}"
            bot.send_message(chat_id=chat_id, text=msg)

        save_scanned_token(token)
        time.sleep(1)  # Rate limiting
