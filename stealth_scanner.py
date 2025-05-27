import sqlite3
import requests
import logging

DB_PATH = "solmad.db"
logger = logging.getLogger(__name__)

# Initialize alerted tokens DB table
def init_alerts_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alerted_tokens (
        token_symbol TEXT PRIMARY KEY
    )''')
    conn.commit()
    conn.close()

def is_token_alerted(token_symbol: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM alerted_tokens WHERE token_symbol = ?", (token_symbol,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_token_alerted(token_symbol: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO alerted_tokens (token_symbol) VALUES (?)", (token_symbol,))
    conn.commit()
    conn.close()

# Example honeypot check (simple contract method inspection)
def check_honeypot(token_address: str) -> bool:
    try:
        # Example API call to fetch contract source or ABI (replace with actual API)
        url = f"https://public-api.solscan.io/account/contracts?account={token_address}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Example suspicious method names
        suspicious_methods = {"setFee", "transferFrom", "blacklist", "pause", "owner"}

        contract_methods = set(m["name"] for m in data.get("methods", []))
        if suspicious_methods.intersection(contract_methods):
            logger.warning(f"Honeypot suspected for token {token_address}: suspicious methods found")
            return True
        return False

    except Exception as e:
        logger.error(f"Error checking honeypot for {token_address}: {e}")
        return False

# Run on a batch of new tokens (simplified example)
def scan_tokens_for_honeypot(token_list):
    alerted = []
    for token in token_list:
        symbol = token.get("symbol")
        address = token.get("address")
        if is_token_alerted(symbol):
            continue  # skip already alerted tokens

        if check_honeypot(address):
            alerted.append(symbol)
            mark_token_alerted(symbol)

    return alerted
