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
    # Users table for limits and tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            daily_spend_limit REAL DEFAULT 1000,
            daily_spent REAL DEFAULT 0,
            last_spent_reset TEXT
        )
    ''')
    # Trade history log
    c.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            trade_type TEXT,
            token_symbol TEXT,
            amount REAL,
            price REAL,
            total_value REAL
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

# User limits and spend tracking

def add_user(user_id, daily_spend_limit=1000):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, daily_spend_limit, daily_spent, last_spent_reset) VALUES (?, ?, ?, ?)",
        (user_id, daily_spend_limit, 0, today)
    )
    conn.commit()
    conn.close()

def get_user_limits(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_spend_limit, daily_spent, last_spent_reset FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        limit, spent, reset_date = row
        today = datetime.date.today().isoformat()
        if reset_date != today:
            reset_daily_spent(user_id)
            spent = 0
        return limit, spent
    else:
        add_user(user_id)
        return 1000, 0

def reset_daily_spent(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("UPDATE users SET daily_spent=0, last_spent_reset=? WHERE user_id=?", (today, user_id))
    conn.commit()
    conn.close()

def update_daily_spent(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET daily_spent = daily_spent + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

# Trade history logging

def log_trade(user_id, trade_type, token_symbol, amount, price):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.datetime.utcnow().isoformat()
    total_value = amount * price
    c.execute('''
        INSERT INTO trade_history (user_id, timestamp, trade_type, token_symbol, amount, price, total_value)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, timestamp, trade_type, token_symbol.upper(), amount, price, total_value))
    conn.commit()
    conn.close()

def get_trade_history(user_id, limit=20):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, trade_type, token_symbol, amount, price, total_value
        FROM trade_history WHERE user_id=?
        ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows
