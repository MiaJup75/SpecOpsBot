import os
import sqlite3

# Use absolute path for DB file (relative to this script)
DB_PATH = os.path.join(os.path.dirname(__file__), "solmad.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Wallet watchlist with labels (nicknames)
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (
        label TEXT PRIMARY KEY,
        address TEXT
    )''')

    # Token tracking list
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        symbol TEXT PRIMARY KEY
    )''')

    conn.commit()
    conn.close()

# WALLET TRACKING
def add_wallet(label, address):
    print(f"[DB] Adding wallet: {label} - {address}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO wallets (label, address) VALUES (?, ?)", (label, address))
    conn.commit()
    conn.close()

def get_wallets():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT label, address FROM wallets")
    results = c.fetchall()
    conn.close()
    print(f"[DB] Retrieved wallets: {results}")
    return results

def remove_wallet(label):
    print(f"[DB] Removing wallet with label: {label}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM wallets WHERE label = ?", (label,))
    conn.commit()
    conn.close()

# TOKEN TRACKING
def add_token(symbol):
    print(f"[DB] Adding token: {symbol.upper()}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO tokens (symbol) VALUES (?)", (symbol.upper(),))
    conn.commit()
    conn.close()

def get_tokens():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT symbol FROM tokens")
    tokens = [row[0] for row in c.fetchall()]
    conn.close()
    print(f"[DB] Retrieved tokens: {tokens}")
    return tokens

def remove_token(symbol):
    print(f"[DB] Removing token: {symbol.upper()}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM tokens WHERE symbol = ?", (symbol.upper(),))
    conn.commit()
    conn.close()
