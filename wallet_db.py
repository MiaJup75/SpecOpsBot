# wallet_db.py – Wallet Watch & Mirror Tracking

import sqlite3

DB_NAME = "solmad.db"

def init_wallet_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            label TEXT,
            address TEXT PRIMARY KEY,
            last_tx TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_wallet(label, address):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO wallets (label, address) VALUES (?, ?)", (label, address))
    conn.commit()
    conn.close()

def remove_wallet(address):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM wallets WHERE address = ?", (address,))
    conn.commit()
    conn.close()

def get_wallets():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT label, address FROM wallets")
    results = c.fetchall()
    conn.close()
    return results

def get_wallet_last_tx(address):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT last_tx FROM wallets WHERE address = ?", (address,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def update_wallet_last_tx(address, last_tx):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE wallets SET last_tx = ? WHERE address = ?", (last_tx, address))
    conn.commit()
    conn.close()

def clear_wallets():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM wallets")
    conn.commit()
    conn.close()
