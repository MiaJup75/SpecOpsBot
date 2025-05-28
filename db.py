import sqlite3
import time

DB_NAME = "solmad.db"

# Initialize all DB tables
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Wallets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            label TEXT,
            address TEXT PRIMARY KEY
        )
    ''')

    # Tokens table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            symbol TEXT PRIMARY KEY
        )
    ''')

    # Trades table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            side TEXT,            -- 'buy' or 'sell'
            token_symbol TEXT,
            amount_sol REAL,
            timestamp INTEGER     -- Unix epoch time (seconds)
        )
    ''')

    # Users table for trade limits etc.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            max_daily_sol REAL DEFAULT 10.0,
            max_single_trade_sol REAL DEFAULT 5.0
        )
    ''')

    conn.commit()
    conn.close()

# Wallets functions
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

# Tokens functions
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

# Users functions
def add_user(user_id: int, max_daily_sol: float = 10.0, max_single_trade_sol: float = 5.0):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users (user_id, max_daily_sol, max_single_trade_sol) 
        VALUES (?, ?, ?)
    ''', (user_id, max_daily_sol, max_single_trade_sol))
    conn.commit()
    conn.close()

def get_user_limits(user_id: int) -> dict:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT max_daily_sol, max_single_trade_sol FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {"max_daily_sol": result[0], "max_single_trade_sol": result[1]}
    else:
        # Defaults if user not found
        return {"max_daily_sol": 10.0, "max_single_trade_sol": 5.0}

# Trades functions
def log_trade(user_id: int, side: str, token_symbol: str, amount_sol: float):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = int(time.time())
    c.execute(
        "INSERT INTO trades (user_id, side, token_symbol, amount_sol, timestamp) VALUES (?, ?, ?, ?, ?)",
        (user_id, side.lower(), token_symbol.upper(), amount_sol, timestamp)
    )
    conn.commit()
    conn.close()

def get_daily_trade_volume(user_id: int) -> float:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    start_of_day = int(time.time()) // 86400 * 86400  # Start of today UTC
    c.execute(
        "SELECT SUM(amount_sol) FROM trades WHERE user_id = ? AND timestamp >= ?",
        (user_id, start_of_day)
    )
    result = c.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0.0

def get_trade_history(user_id: int, limit: int = 10) -> list:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT side, token_symbol, amount_sol, timestamp FROM trades WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )
    rows = c.fetchall()
    conn.close()
    # Format trades as list of dicts with readable time
    history = []
    for side, symbol, amount, ts in rows:
        history.append({
            "side": side,
            "token_symbol": symbol,
            "amount_sol": amount,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))
        })
    return history
