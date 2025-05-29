# config.py – Environment-based config for deployment

import os

# Use environment variable first, fallback to hardcoded value if needed
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_FALLBACK_TOKEN_HERE")
SQLITE_PATH = os.getenv("SQLITE_PATH", "tokens.db")
