from telegram import Update
from telegram.ext import CallbackContext
from db import get_user_limits, set_user_limits, get_trade_history
from trade_executor import TradeExecutor
import logging

logger = logging.getLogger(__name__)
trade_executor = TradeExecutor()

def execute_sell_command(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    args = context.args

    if len(args) < 2:
        update.message.reply_text("Usage: /sell <TOKEN_SYMBOL> <AMOUNT>")
        return

    token_symbol = args[0].upper()
    try:
        amount = float(args[1])
    except ValueError:
        update.message.reply_text("Amount must be a number.")
        return

    # Simulate getting current price - in production fetch real price from API
    current_price = 0.00003  # Placeholder, replace with live price fetch

    # Enhanced stop loss logic: compare with user average buy price if available
    limits = get_user_limits(user_id)
    stop_loss_pct = limits.get("stop_loss_pct")
    avg_buy_price = get_avg_buy_price(user_id, token_symbol)  # You need to implement this in your DB

    if avg_buy_price and stop_loss_pct:
        price_drop_pct = ((avg_buy_price - current_price) / avg_buy_price) * 100
        if price_drop_pct >= stop_loss_pct:
            update.message.reply_text(
                f"⚠️ Cannot sell. Current price dropped {price_drop_pct:.2f}% below your avg buy price "
                f"which exceeds your stop loss of {stop_loss_pct}%."
            )
            return

    # Attempt trade execution
    success = trade_executor.execute_sell(user_id, token_symbol, amount, current_price)
    if success:
        update.message.reply_text(f"✅ Sold {amount} {token_symbol} at ${current_price:.6f} per token.")
    else:
        update.message.reply_text("❌ Trade failed or limits exceeded.")

def view_limits_command(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    limits = get_user_limits(user_id)
    daily_limit = limits.get("daily_sell_limit", "Not set")
    stop_loss = limits.get("stop_loss_pct", "Not set")

    msg = (
        f"📊 Your Trade Limits:\n"
        f"• Daily Sell Limit: {daily_limit}\n"
        f"• Stop Loss %: {stop_loss}\n"
        f"\nUse /setlimit <daily_sell_limit> <stop_loss_pct> to update."
    )
    update.message.reply_text(msg)

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

# Placeholder function you need to implement in your DB to fetch average buy price
def get_avg_buy_price(user_id: str, token_symbol: str) -> float | None:
    # Example: query your trades table for average buy price of token for user
    # Return None if no data
    return None
