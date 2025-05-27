import sqlite3

def init_db():
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()

    # Wallet watchlist with labels
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (
        label TEXT,
        address TEXT PRIMARY KEY
    )''')

    # Token tracking list
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        symbol TEXT PRIMARY KEY
    )''')

    conn.commit()
    conn.close()

# WALLET TRACKING
def add_wallet(label, address):
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO wallets (label, address) VALUES (?, ?)", (label, address))
    conn.commit()
    conn.close()

def get_wallets():
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("SELECT label, address FROM wallets")
    results = c.fetchall()
    conn.close()
    return results

# TOKEN TRACKING
def add_token(symbol):
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO tokens (symbol) VALUES (?)", (symbol.upper(),))
    conn.commit()
    conn.close()

def get_tokens():
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("SELECT symbol FROM tokens")
    tokens = [row[0] for row in c.fetchall()]
    conn.close()
    return tokens

def remove_token(symbol):
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("DELETE FROM tokens WHERE symbol = ?", (symbol.upper(),))
    conn.commit()
    conn.close()
