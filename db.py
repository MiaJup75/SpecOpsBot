import sqlite3
from datetime import datetime, date

DB_NAME = "solmad.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Wallet watchlist with labels
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            label TEXT,
            address TEXT PRIMARY KEY
        )
    ''')
    # Token tracking list
    c.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            symbol TEXT PRIMARY KEY
        )
    ''')

    # Trades table for trade execution logging
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            token_symbol TEXT,
            amount REAL,
            side TEXT,
            price REAL,
            timestamp TEXT
        )
    ''')

    # Users table for customizable limits
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            daily_sell_limit REAL DEFAULT 10000,
            stop_loss_pct REAL DEFAULT 10
        )
    ''')

    conn.commit()
    conn.close()

def add_wallet(label, address):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO wallets (label, address) VALUES (?, ?)", (label, address))
    conn.commit()
    conn.close()

def get_wallets():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT label, address FROM wallets")
    results = c.fetchall()
    conn.close()
    return results

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

def log_trade(user_id: str, token_symbol: str, amount: float, side: str, price: float | None, timestamp: datetime):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO trades (user_id, token_symbol, amount, side, price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, token_symbol.upper(), amount, side, price, timestamp.isoformat()))
    conn.commit()
    conn.close()

def get_trade_history(user_id: str, token_symbol: str, start_date: date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT user_id, token_symbol, amount, side, price, timestamp FROM trades
        WHERE user_id = ? AND token_symbol = ? AND date(timestamp) >= ?
    """, (user_id, token_symbol.upper(), start_date.isoformat()))
    rows = c.fetchall()
    conn.close()
    trades = []
    for row in rows:
        trades.append({
            "user_id": row[0],
            "token_symbol": row[1],
            "amount": row[2],
            "side": row[3],
            "price": row[4],
            "timestamp": datetime.fromisoformat(row[5])
        })
    return trades

def get_user_limits(user_id: str) -> dict:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT daily_sell_limit, stop_loss_pct FROM users WHERE user_id = ?
    """, (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"daily_sell_limit": row[0], "stop_loss_pct": row[1]}
    else:
        # Return defaults if no user set limits found
        return {"daily_sell_limit": 10000, "stop_loss_pct": 10}

def set_user_limits(user_id: str, daily_sell_limit: float, stop_loss_pct: float):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (user_id, daily_sell_limit, stop_loss_pct)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            daily_sell_limit=excluded.daily_sell_limit,
            stop_loss_pct=excluded.stop_loss_pct
    """, (user_id, daily_sell_limit, stop_loss_pct))
    conn.commit()
    conn.close()
