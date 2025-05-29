# pnl.py – Profit and Loss Tracker

from db import get_trade_history

def get_pnl_report(user_id):
    trades_by_token = {}
    all_trades = get_trade_history(user_id, None)  # Get all trades

    for trade in all_trades:
        token = trade['token_symbol']
        if token not in trades_by_token:
            trades_by_token[token] = []
        trades_by_token[token].append(trade)

    report_lines = ["<b>📊 PnL Report</b>"]

    for token, trades in trades_by_token.items():
        buys = [t for t in trades if t['side'] == 'buy']
        sells = [t for t in trades if t['side'] == 'sell']
        total_buy = sum(t['amount'] * t['price'] for t in buys)
        total_sell = sum(t['amount'] * t['price'] for t in sells)
        net_qty = sum(t['amount'] if t['side'] == 'buy' else -t['amount'] for t in trades)

        if total_buy == 0:
            continue

        avg_buy_price = total_buy / sum(t['amount'] for t in buys)
        avg_sell_price = total_sell / sum(t['amount'] for t in sells) if sells else 0
        net_pnl = total_sell - total_buy

        report_lines.append(
            f"\n<b>{token}</b>\nQty: {net_qty:.2f} | Buy@ ${avg_buy_price:.4f} | Sell@ ${avg_sell_price:.4f}\n💰 PnL: ${net_pnl:.2f}"
        )

    return "\n".join(report_lines) if len(report_lines) > 1 else "No trade data found."


# scorecard.py – Post-Launch Scorecard Generator

def generate_token_scorecard(token):
    score = 0
    criteria = []

    if token.get("market_cap", 0) < 500000:
        score += 1
        criteria.append("✅ Low MCap")
    if token.get("liquidity", 0) > 30000:
        score += 1
        criteria.append("✅ Healthy LP")
    if token.get("volume", 0) > 100000:
        score += 1
        criteria.append("✅ Active Volume")
    if token.get("holders", 0) > 1000:
        score += 1
        criteria.append("✅ Growing Community")
    if not token.get("honeypot", False):
        score += 1
        criteria.append("✅ Not a Honeypot")

    result = f"<b>📈 Scorecard for {token.get('symbol', '?')}</b>\nScore: {score}/5\n" + "\n".join(criteria)
    return result


# ux.py – UX Command Handlers for /start and /help

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

def handle_start_command(update: Update, context: CallbackContext):
    welcome_msg = """
<b>🤖 Welcome to SolMadSpecBot!</b>

Use the buttons or commands below to get started:

/start – Show this menu
/help – List available commands
/max – MAX token stats
/wallets – Tracked wallets
/watch – Add a wallet to watch
/tokens – Show watched tokens
/addtoken $TOKEN – Add token
/removetoken $TOKEN – Remove token
/trending – Top meme coins
/new – New launches
/alerts – Suspicious activity
/pnl – PnL report

Tip: Use inline buttons or type commands directly.
"""
    update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)

def handle_help_command(update: Update, context: CallbackContext):
    help_msg = """
<b>📘 Help Menu</b>

/start – Welcome screen
/help – This help menu
/max – MAX token stats
/watch [label] [address] – Track wallet
/wallets – View wallet list
/tokens – Watched tokens
/addtoken $TOKEN – Watch token
/removetoken $TOKEN – Remove token
/trending – Top trending
/new – New launches
/alerts – Suspicious activity
/pnl – Trade profit/loss
"""
    update.message.reply_text(help_msg, parse_mode=ParseMode.HTML)
