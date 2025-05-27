import logging
import time

logger = logging.getLogger(__name__)

def safe_request(func, *args, retries=3, delay=2, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Request failed (attempt {attempt}): {e}")
            if attempt == retries:
                logger.error(f"Max retries reached. Giving up.")
                raise
            time.sleep(delay)

def safe_send_message(bot, chat_id, text, **kwargs):
    for attempt in range(1, 4):
        try:
            return bot.send_message(chat_id=chat_id, text=text, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to send message (attempt {attempt}): {e}")
            if attempt == 3:
                logger.error("Giving up sending message.")
                raise
            time.sleep(2)
