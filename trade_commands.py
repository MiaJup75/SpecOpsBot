from telegram import Update
from telegram.ext import CallbackContext
from db import get_user_limits, set_user_limits, get_trade_history

def view_limits_command(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    limits = get_user_limits(user_id)
    daily_limit = limits.get("daily_sell_limit", "Not set")
    stop_loss = limits.get("stop_loss_pct", "Not set")

    msg = (
        "📊 Your Trade Limits:\n"
        f"• Daily Sell Limit: <b>{daily_limit}</b>\n"
        f"• Stop Loss %: <b>{stop_loss}</b>\n"
        "\nUse /setlimit &lt;daily_sell_limit&gt; &lt;stop_loss_pct&gt; to update."
    )
    update.message.reply_text(msg, parse_mode="HTML")

def set_limits_command(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    args = context.args

    if len(args) != 2:
        update.message.reply_text("Usage: /setlimit <daily_sell_limit> <stop_loss_pct>")
        return

    try:
        daily_limit = float(args[0])
        stop_loss_pct = float(args[1])
    except ValueError:
        update.message.reply_text("Both limits must be numbers.")
        return

    set_user_limits(user_id, daily_limit, stop_loss_pct)
    update.message.reply_text(f"✅ Limits updated: Daily Sell Limit = {daily_limit}, Stop Loss = {stop_loss_pct}%")

def trade_history_command(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    token_symbol = context.args[0].upper() if context.args else None

    if not token_symbol:
        update.message.reply_text("Usage: /tradehistory <TOKEN_SYMBOL>")
        return

    trades = get_trade_history(user_id, token_symbol)
    if not trades:
        update.message.reply_text(f"No trade history found for {token_symbol}.")
        return

    msg = f"📜 Trade History for {token_symbol}:\n"
    for t in trades:
        timestamp = t['timestamp'].strftime("%Y-%m-%d %H:%M")
        msg += f"• {t['side'].capitalize()} {t['amount']} @ {t.get('price', 'N/A')} on {timestamp}\n"
    update.message.reply_text(msg)
