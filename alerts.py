# alerts.py – Suspicious Activity Alerts Module

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

def get_suspicious_activity_alerts():
    # Replace this with real detection logic or hooks
    alerts = [
        "🚨 Whale wallet 9xJd... dumped 500K tokens.",
        "⚠️ Dev wallet moved LP tokens.",
        "👀 Sudden spike in sell volume for $PEPE2."
    ]
    return "<b>🚨 Suspicious Activity Alerts</b>\n\n" + "\n".join(alerts)

def handle_alerts_command(update: Update, context: CallbackContext):
    try:
        msg = get_suspicious_activity_alerts()
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        update.message.reply_text("⚠️ Failed to fetch alerts.")
        print(f"Error in handle_alerts_command: {e}")
