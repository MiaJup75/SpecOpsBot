import requests
import logging

logger = logging.getLogger(__name__)

# Example: get Telegram mentions count for a token symbol from a hypothetical API
def get_telegram_mentions(token_symbol: str) -> int:
    try:
        # Replace with real Telegram API or third-party service
        url = f"https://api.example.com/telegram/mentions?token={token_symbol}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return int(data.get("mention_count", 0))
    except Exception as e:
        logger.error(f"Failed to fetch Telegram mentions for {token_symbol}: {e}")
        return 0

# Example: get Twitter (X) mentions count for a token symbol
def get_twitter_mentions(token_symbol: str) -> int:
    try:
        # Replace with real Twitter API or scraping service
        url = f"https://api.example.com/twitter/mentions?token={token_symbol}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return int(data.get("mention_count", 0))
    except Exception as e:
        logger.error(f"Failed to fetch Twitter mentions for {token_symbol}: {e}")
        return 0

# Aggregate score for social signals
def get_social_signal_score(token_symbol: str) -> int:
    tg = get_telegram_mentions(token_symbol)
    tw = get_twitter_mentions(token_symbol)
    score = tg + tw
    logger.info(f"Social score for {token_symbol}: Telegram={tg}, Twitter={tw}, Total={score}")
    return score
