import sqlite3
import logging

logger = logging.getLogger(__name__)

DB_NAME = "specopsbot.db"

def get_wallets():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT label, address FROM wallets")
        results = [row for row in c.fetchall()]
    except sqlite3.OperationalError:
        # fallback for legacy schema
        c.execute("SELECT address FROM wallets")
        results = [("", row[0]) for row in c.fetchall()]
    conn.close()
    return results

def get_wallet_last_tx(address: str) -> str | None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT last_tx FROM wallets WHERE address = ?", (address,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def update_wallet_last_tx(address: str, last_tx: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE wallets SET last_tx = ? WHERE address = ?", (last_tx, address))
    conn.commit()
    conn.close()

def add_wallet(label, address):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO wallets (label, address) VALUES (?, ?)", (label, address))
    except sqlite3.OperationalError:
        # fallback if old schema without label
        c.execute("INSERT OR IGNORE INTO wallets (address) VALUES (?)", (address,))
    conn.commit()
    conn.close()

def remove_wallet(label_or_address):
    """Remove wallet by label or address."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Try to remove by address
    c.execute("DELETE FROM wallets WHERE address = ?", (label_or_address,))
    # Also remove by label in case user provided the nickname
    c.execute("DELETE FROM wallets WHERE label = ?", (label_or_address,))
    conn.commit()
    conn.close()

def add_token(symbol):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO tokens (symbol) VALUES (?)", (symbol.upper(),))
    conn.commit()
    conn.close()

def get_tokens():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT symbol FROM tokens")
    tokens = [row[0] for row in c.fetchall()]
    conn.close()
    return tokens

def remove_token(symbol):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tokens WHERE symbol = ?", (symbol.upper(),))
    conn.commit()
    conn.close()

def get_user_limits(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_sell_limit, stop_loss_pct FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"daily_sell_limit": row[0], "stop_loss_pct": row[1]}
    else:
        return {"daily_sell_limit": None, "stop_loss_pct": None}

def set_user_limits(user_id, daily_sell_limit, stop_loss_pct):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (user_id, daily_sell_limit, stop_loss_pct) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET daily_sell_limit = excluded.daily_sell_limit, stop_loss_pct = excluded.stop_loss_pct",
        (user_id, daily_sell_limit, stop_loss_pct),
    )
    conn.commit()
    conn.close()

def log_trade(user_id, token_symbol, side, amount, price):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO trades (user_id, token_symbol, side, amount, price) VALUES (?, ?, ?, ?, ?)",
        (user_id, token_symbol, side, amount, price),
    )
    conn.commit()
    conn.close()

def get_trade_history(user_id, token_symbol):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT side, amount, price, timestamp FROM trades WHERE user_id = ? AND token_symbol = ? ORDER BY timestamp DESC",
        (user_id, token_symbol),
    )
    rows = c.fetchall()
    conn.close()
    trades = []
    for row in rows:
        trades.append({
            "side": row[0],
            "amount": row[1],
            "price": row[2],
            "timestamp": row[3],
        })
    return trades

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Wallets
    try:
        c.execute("CREATE TABLE IF NOT EXISTS wallets (label TEXT, address TEXT UNIQUE, last_tx TEXT)")
    except Exception as e:
        logger.error(f"Error creating wallets table: {e}")
    # Tokens
    try:
        c.execute("CREATE TABLE IF NOT EXISTS tokens (symbol TEXT UNIQUE)")
    except Exception as e:
        logger.error(f"Error creating tokens table: {e}")
    # Users
    try:
        c.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, daily_sell_limit REAL, stop_loss_pct REAL)")
    except Exception as e:
        logger.error(f"Error creating users table: {e}")
    # Trades
    try:
        c.execute("CREATE TABLE IF NOT EXISTS trades (user_id TEXT, token_symbol TEXT, side TEXT, amount REAL, price REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    except Exception as e:
        logger.error(f"Error creating trades table: {e}")
    conn.commit()
    conn.close()
