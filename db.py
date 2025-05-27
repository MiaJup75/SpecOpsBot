import sqlite3
import os
from datetime import datetime

DB_FILE = "solmad.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS watched_wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT,
        address TEXT UNIQUE
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS watched_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE,
        added_at TEXT
    )""")
    conn.commit()
    conn.close()

def add_wallet(label, address):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO watched_wallets (label, address) VALUES (?, ?)", (label, address))
        conn.commit()
    finally:
        conn.close()

def get_wallets():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT label, address FROM watched_wallets")
    rows = c.fetchall()
    conn.close()
    return rows

def add_token(symbol):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO watched_tokens (symbol, added_at) VALUES (?, ?)", (symbol.upper(), datetime.utcnow().isoformat()))
        conn.commit()
    finally:
        conn.close()

def get_tokens():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT symbol FROM watched_tokens")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]
