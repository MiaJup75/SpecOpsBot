import os
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

# Keep track of last alerts sent to avoid spam
_last_botnet_alerts = set()

def fetch_suspicious_botnet_data():
    # TODO: Replace with real API calls or detection logic
    # Example suspicious alerts
    return [
        {"token": "FAKE", "alert": "Botnet detected trading activity"},
        {"token": "SCAM", "alert": "Abnormal volume spike by bots"}
    ]

def check_botnet_activity(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    alerts = fetch_suspicious_botnet_data()

    for alert in alerts:
        alert_key = f"{alert['token']}:{alert['alert']}"
        if alert_key not in _last_botnet_alerts:
            try:
                bot.send_message(chat_id=chat_id, text=f"🚨 {alert['alert']} on ${alert['token']}")
                _last_botnet_alerts.add(alert_key)
            except Exception as e:
                logger.error(f"[Botnet] Error sending alert: {e}")
