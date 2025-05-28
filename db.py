import sqlite3
import datetime

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
    # User trade limits table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_limits (
            user_id TEXT PRIMARY KEY,
            daily_sell_limit REAL,
            stop_loss_pct REAL
        )
    ''')
    # Trade history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            token_symbol TEXT,
            side TEXT,
            amount REAL,
            price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Wallets
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

# Tokens
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

# User Limits
def get_user_limits(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_sell_limit, stop_loss_pct FROM user_limits WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"daily_sell_limit": row[0], "stop_loss_pct": row[1]}
    else:
        return {}

def set_user_limits(user_id, daily_sell_limit, stop_loss_pct):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_limits (user_id, daily_sell_limit, stop_loss_pct)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            daily_sell_limit=excluded.daily_sell_limit,
            stop_loss_pct=excluded.stop_loss_pct
    """, (user_id, daily_sell_limit, stop_loss_pct))
    conn.commit()
    conn.close()

# Trade History
def log_trade(user_id, token_symbol, side, amount, price):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO trade_history (user_id, token_symbol, side, amount, price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, token_symbol, side, amount, price, datetime.datetime.utcnow()))
    conn.commit()
    conn.close()

def get_trade_history(user_id, token_symbol):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT side, amount, price, timestamp FROM trade_history
        WHERE user_id = ? AND token_symbol = ?
        ORDER BY timestamp DESC
        LIMIT 50
    """, (user_id, token_symbol))
    rows = c.fetchall()
    conn.close()
    # Convert to list of dicts
    trades = []
    for row in rows:
        trades.append({
            "side": row[0],
            "amount": row[1],
            "price": row[2],
            "timestamp": row[3],
        })
    return trades

def get_daily_trade_volume(user_id, token_symbol):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.datetime.utcnow().date()
    start_time = datetime.datetime.combine(today, datetime.time.min)
    c.execute("""
        SELECT SUM(amount) FROM trade_history
        WHERE user_id = ? AND token_symbol = ? AND side = 'sell' AND timestamp >= ?
    """, (user_id, token_symbol, start_time))
    result = c.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0
