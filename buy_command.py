from telegram import Update
from telegram.ext import CallbackContext
from trade_executor import TradeExecutor

def buy_command(update: Update, context: CallbackContext) -> None:
    """
    Usage: /buy TOKEN_SYMBOL AMOUNT PRICE
    Example: /buy MAX 1000 0.000025
    """
    if len(context.args) != 3:
        update.message.reply_text("Usage: /buy TOKEN_SYMBOL AMOUNT PRICE\nExample: /buy MAX 1000 0.000025")
        return
    
    token_symbol = context.args[0].upper()
    try:
        amount = float(context.args[1])
        price = float(context.args[2])
    except ValueError:
        update.message.reply_text("⚠️ Amount and price must be valid numbers.")
        return

    user_id = update.effective_user.id
    executor = TradeExecutor(user_id)
    
    update.message.reply_text(f"⏳ Attempting to buy {amount} {token_symbol} at price {price}...")
    success = executor.execute_buy(token_symbol, amount, price)

    if success:
        update.message.reply_text(f"✅ Buy order executed: {amount} {token_symbol} at ${price:.6f}")
    else:
        update.message.reply_text("❌ Buy order failed or exceeded limits.")
