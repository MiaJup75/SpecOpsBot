import sqlite3
import json
from datetime import datetime

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

    # Wallet activity cache for mirror wallet detection
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallet_activity_cache (
            address TEXT PRIMARY KEY,
            activity_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # User limits for trade execution
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            daily_sell_limit REAL DEFAULT 0,
            stop_loss_pct REAL DEFAULT 0
        )
    ''')

    # Trade history log
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            token_symbol TEXT,
            side TEXT,
            amount REAL,
            price REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def get_wallet_activity_cache(address: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT activity_json FROM wallet_activity_cache WHERE address = ?", (address,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except Exception:
            return None
    return None

def update_wallet_activity_cache(address: str, activity: dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    activity_json = json.dumps(activity)
    now = datetime.utcnow()
    c.execute('''
        INSERT INTO wallet_activity_cache(address, activity_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(address) DO UPDATE SET
            activity_json=excluded.activity_json,
            updated_at=excluded.updated_at
    ''', (address, activity_json, now))
    conn.commit()
    conn.close()

# User limits functions
def get_user_limits(user_id: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_sell_limit, stop_loss_pct FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"daily_sell_limit": row[0], "stop_loss_pct": row[1]}
    else:
        return {"daily_sell_limit": None, "stop_loss_pct": None}

def set_user_limits(user_id: str, daily_sell_limit: float, stop_loss_pct: float):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO users(user_id, daily_sell_limit, stop_loss_pct)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            daily_sell_limit=excluded.daily_sell_limit,
            stop_loss_pct=excluded.stop_loss_pct
    ''', (user_id, daily_sell_limit, stop_loss_pct))
    conn.commit()
    conn.close()

# Trade history functions
def log_trade(user_id: str, token_symbol: str, side: str, amount: float, price: float):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.utcnow()
    c.execute('''
        INSERT INTO trades(user_id, token_symbol, side, amount, price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, token_symbol.upper(), side, amount, price, now))
    conn.commit()
    conn.close()

def get_trade_history(user_id: str, token_symbol: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT side, amount, price, timestamp
        FROM trades
        WHERE user_id = ? AND token_symbol = ?
        ORDER BY timestamp DESC
    ''', (user_id, token_symbol.upper()))
    rows = c.fetchall()
    conn.close()
    trades = []
    for row in rows:
        trades.append({
            "side": row[0],
            "amount": row[1],
            "price": row[2],
            "timestamp": datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
        })
    return trades
