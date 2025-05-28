import os
import requests
from telegram import Bot
import logging
import time

logger = logging.getLogger(__name__)

# Keep track of last alert times per token to throttle repeated alerts
_last_alert_times = {}
ALERT_COOLDOWN_SECONDS = 1800  # 30 minutes cooldown

def can_alert(token_symbol: str) -> bool:
    now = time.time()
    last_alert = _last_alert_times.get(token_symbol)
    if last_alert and now - last_alert < ALERT_COOLDOWN_SECONDS:
        return False
    _last_alert_times[token_symbol] = now
    return True

def check_botnet_activity(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    # Example suspicious activity tokens/messages
    alerts = [
        ("FAKE", "Botnet detected suspicious activity on $FAKE"),
        ("SCAM", "Unusual volume spikes on $SCAM"),
    ]
    try:
        for token, message in alerts:
            if can_alert(token):
                bot.send_message(chat_id=chat_id, text=f"🚨 {message}")
    except Exception as e:
        logger.error(f"[Botnet] Error during botnet activity check: {e}")
