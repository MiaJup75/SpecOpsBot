# botnet.py – Botnet Detection Handler with Cooldown Throttling

import os
import time
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

# Alert cooldown system to avoid spam (per token)
_last_alert_times = {}
ALERT_COOLDOWN_SECONDS = 1800  # 30 minutes

def can_alert(token_symbol: str) -> bool:
    """Throttle repeated alerts for the same token within cooldown window."""
    now = time.time()
    last_alert = _last_alert_times.get(token_symbol)
    if last_alert and now - last_alert < ALERT_COOLDOWN_SECONDS:
        return False
    _last_alert_times[token_symbol] = now
    return True

def check_botnet_activity(bot: Bot):
    """Simulate detection and send alerts for suspicious botnet activity."""
    chat_id = os.getenv("CHAT_ID")
    alerts = [
        ("FAKE", "Botnet detected suspicious activity on $FAKE"),
        ("SCAM", "Unusual volume spikes on $SCAM"),
    ]
    try:
        for token, message in alerts:
            if can_alert(token):
                bot.send_message(chat_id=chat_id, text=f"🚨 {message}")
    except Exception as e:
        logger.error(f"[Botnet] Error sending botnet alert: {e}")
