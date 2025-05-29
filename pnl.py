from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from db import get_trade_history


def get_pnl_report(user_id, token_symbol):
    trades = get_trade_history(user_id, token_symbol)
    if not trades:
        return f"No trades found for ${token_symbol}."

    buys = [t for t in trades if t['side'] == 'BUY']
    sells = [t for t in trades if t['side'] == 'SELL']

    total_buy = sum(t['amount'] * t['price'] for t in buys)
    total_buy_qty = sum(t['amount'] for t in buys)
    total_sell = sum(t['amount'] * t['price'] for t in sells)
    total_sell_qty = sum(t['amount'] for t in sells)

    avg_buy_price = total_buy / total_buy_qty if total_buy_qty > 0 else 0
    avg_sell_price = total_sell / total_sell_qty if total_sell_qty > 0 else 0
    realized_pnl = total_sell - (total_sell_qty * avg_buy_price)

    report = f"<b>💹 PnL Report for ${token_symbol.upper()}</b>\n\n"
    report += f"<b>Total Buys:</b> {total_buy_qty:.2f} at avg ${avg_buy_price:.4f}\n"
    report += f"<b>Total Sells:</b> {total_sell_qty:.2f} at avg ${avg_sell_price:.4f}\n"
    report += f"<b>Realized PnL:</b> ${realized_pnl:.2f}"
    return report


def handle_pnl_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if len(context.args) != 1:
        update.message.reply_text("Usage: /pnl $TOKEN")
        return

    symbol = context.args[0].lstrip("$")
    report = get_pnl_report(user_id, symbol)
    update.message.reply_text(report, parse_mode=ParseMode.HTML)
