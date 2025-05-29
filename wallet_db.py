# wallet_db.py – Tracks watched wallets using SQLite

import sqlite3
import os

DB_PATH = os.getenv("SQLITE_PATH", "tokens.db")

def init_wallet_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                address TEXT NOT NULL UNIQUE
            );
        """)
        conn.commit()

def add_wallet(label: str, address: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO wallets (label, address) VALUES (?, ?)", (label, address))
        conn.commit()

def get_wallets():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT label, address FROM wallets ORDER BY id DESC")
        return cur.fetchall()

def remove_wallet(address: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM wallets WHERE address = ?", (address,))
        conn.commit()
