import os
import requests
import logging
from telegram import Bot
from time import time

logger = logging.getLogger(__name__)

_last_alert_time = 0
ALERT_COOLDOWN_SECONDS = 1800  # 30 minutes

def fetch_suspicious_activity():
    # Example: replace with real API or logic to get suspicious wallets or tokens
    # Return a list of strings (alerts)
    return [
        "Botnet detected activity on $FAKE",
        "Suspicious volume on $SCAM",
    ]

def check_botnet_activity(bot: Bot):
    global _last_alert_time
    chat_id = os.getenv("CHAT_ID")
    now = time()
    if now - _last_alert_time < ALERT_COOLDOWN_SECONDS:
        return  # Skip alert to avoid spam

    try:
        alerts = fetch_suspicious_activity()
        for alert in alerts:
            bot.send_message(chat_id=chat_id, text=f"🚨 {alert}")
        _last_alert_time = now
    except Exception as e:
        logger.error(f"[Botnet] Error during botnet activity check: {e}")
