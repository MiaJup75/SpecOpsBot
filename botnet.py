import os
import requests
from telegram import Bot
import logging
from time import time

logger = logging.getLogger(__name__)

_alerted_tokens = {}
ALERT_COOLDOWN = 1800  # 30 minutes cooldown

def fetch_botnet_alerts():
    # Placeholder: Replace with real API or logic to get suspicious tokens and alerts
    # Example return: [{"token": "FAKE", "alert": "Botnet detected activity"}, ...]
    try:
        # Example static, replace with your real data fetch
        return [
            {"token": "FAKE", "alert": "Botnet detected activity"},
            {"token": "SCAM", "alert": "Suspicious volume detected"},
        ]
    except Exception as e:
        logger.error(f"[Botnet] Failed to fetch alerts: {e}")
        return []

def check_botnet_activity(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    alerts = fetch_botnet_alerts()
    now = time()

    for alert_info in alerts:
        token = alert_info["token"]
        alert_msg = alert_info["alert"]

        # Check cooldown
        last_alert_time = _alerted_tokens.get(token)
        if last_alert_time and (now - last_alert_time) < ALERT_COOLDOWN:
            continue  # Skip repeated alert within cooldown

        # Send alert
        try:
            bot.send_message(chat_id=chat_id, text=f"🚨 {alert_msg} on ${token}")
            _alerted_tokens[token] = now
        except Exception as e:
            logger.error(f"[Botnet] Error sending alert for {token}: {e}")
