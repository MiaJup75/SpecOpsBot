# Add columns nickname and description to tokens table
def init_db():
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS wallets (
        label TEXT,
        address TEXT PRIMARY KEY
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        symbol TEXT PRIMARY KEY,
        nickname TEXT,
        description TEXT
    )''')

    conn.commit()
    conn.close()

def add_token(symbol, nickname=None, description=None):
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO tokens (symbol, nickname, description)
        VALUES (?, ?, ?)
    """, (symbol.upper(), nickname, description))
    conn.commit()
    conn.close()

def get_tokens():
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("SELECT symbol, nickname, description FROM tokens")
    results = c.fetchall()
    conn.close()
    return results

def remove_token(symbol):
    conn = sqlite3.connect("solmad.db")
    c = conn.cursor()
    c.execute("DELETE FROM tokens WHERE symbol = ?", (symbol.upper(),))
    conn.commit()
    conn.close()
