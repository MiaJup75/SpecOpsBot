import os
import requests
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

# Cache alerts to avoid spamming repeat messages
_alert_cache = {}

ALERT_COOLDOWN = 1800  # seconds, e.g. 30 minutes

def fetch_suspicious_activity():
    """
    Placeholder function to fetch suspicious activity data.
    Replace with real API endpoint or implement custom logic.
    Expected return: list of dicts like
    [{'token': 'FAKE', 'alert': 'Botnet detected activity', 'timestamp': 1234567890}, ...]
    """
    # Example static data for demo
    return [
        {"token": "FAKE", "alert": "Botnet detected activity on $FAKE", "timestamp": 0},
        {"token": "SCAM", "alert": "Suspicious volume on $SCAM", "timestamp": 0},
    ]

def should_alert(token_key, timestamp):
    """Check cooldown cache to prevent alert spam."""
    import time
    now = time.time()
    last_alert = _alert_cache.get(token_key)
    if last_alert and now - last_alert < ALERT_COOLDOWN:
        return False
    _alert_cache[token_key] = now
    return True

def check_botnet_activity(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    try:
        suspicious_events = fetch_suspicious_activity()
        for event in suspicious_events:
            token = event.get("token")
            alert_text = event.get("alert")
            ts = event.get("timestamp", 0)

            token_key = f"{token}_{alert_text}"
            if should_alert(token_key, ts):
                message = f"🚨 {alert_text}"
                bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.error(f"[Botnet] Error during botnet activity check: {e}")
