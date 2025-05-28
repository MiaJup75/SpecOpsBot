import os
import requests
from telegram import Bot
import logging
from time import time

logger = logging.getLogger(__name__)
ALERT_COOLDOWN_SECONDS = 1800  # 30 mins

_last_alert_times = {}

def should_alert(alert_key):
    now = time()
    last_alert = _last_alert_times.get(alert_key)
    if last_alert and now - last_alert < ALERT_COOLDOWN_SECONDS:
        return False
    _last_alert_times[alert_key] = now
    return True

def fetch_suspicious_activity():
    # Replace with actual suspicious activity feed or API
    # For demo, return static list
    return [
        {"type": "botnet", "token": "FAKE", "detail": "Unusual bot trading detected"},
        {"type": "volume_spike", "token": "SCAM", "detail": "Suspicious volume increase"},
    ]

def check_botnet_activity(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    try:
        alerts = fetch_suspicious_activity()
        for alert in alerts:
            key = f"{alert['type']}_{alert['token']}"
            if not should_alert(key):
                continue
            msg = f"🚨 Botnet Alert on ${alert['token']} — {alert['detail']}"
            bot.send_message(chat_id=chat_id, text=msg)
    except Exception as e:
        logger.error(f"[Botnet] Error during botnet activity check: {e}")
