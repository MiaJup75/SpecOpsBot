from telegram import Update
from telegram.ext import CallbackContext
from db import get_user_limits, set_user_limits, get_trade_history

def view_limits_command(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    limits = get_user_limits(user_id)
    daily_limit = limits.get("daily_sell_limit", "Not set")
    stop_loss = limits.get("stop_loss_pct", "Not set")

    msg = (
        f"📊 <b>Your Trade Limits</b>:\n"
        f"• Daily Sell Limit: {daily_limit}\n"
        f"• Stop Loss %: {stop_loss}\n\n"
        "Use /setlimit <daily_sell_limit> <stop_loss_pct> to update your limits."
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
        update.message.reply_text("Both limits must be valid numbers.")
        return

    set_user_limits(user_id, daily_limit, stop_loss_pct)
    update.message.reply_text(
        f"✅ Limits updated:\nDaily Sell Limit = {daily_limit}\nStop Loss = {stop_loss_pct}%",
        parse_mode="HTML"
    )

def trade_history_command(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    if not context.args:
        update.message.reply_text("Usage: /tradehistory <TOKEN_SYMBOL>")
        return
    token_symbol = context.args[0].upper()

    trades = get_trade_history(user_id, token_symbol)
    if not trades:
        update.message.reply_text(f"No trade history found for {token_symbol}.")
        return

    msg = f"📜 <b>Trade History for {token_symbol}</b>:\n"
    for t in trades:
        timestamp = t['timestamp'].strftime("%Y-%m-%d %H:%M")
        msg += f"• {t['side'].capitalize()} {t['amount']} @ {t.get('price', 'N/A')} on {timestamp}\n"
    update.message.reply_text(msg, parse_mode="HTML")
