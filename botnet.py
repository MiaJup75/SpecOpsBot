import logging

logger = logging.getLogger(__name__)

def detect_botnet_activity(bot):
    """
    Detects suspicious buy/sell bot activity from on-chain patterns.
    Alerts the chat if detected.
    """
    # TODO: Implement logic with real data from blockchain or analytics APIs

    suspicious_activity = [
        {"token": "FAKE", "activity": "Large sudden sell orders by bots"},
        {"token": "SCAM", "activity": "Bot-driven wash trading detected"},
    ]

    for event in suspicious_activity:
        msg = f"🚨 <b>Botnet Alert:</b> Suspicious activity detected on {event['token']}\n" \
              f"Details: {event['activity']}"
        logger.info(f"Botnet alert: {event['token']}")
        bot.send_message(chat_id=bot.chat_id, text=msg, parse_mode="HTML")
