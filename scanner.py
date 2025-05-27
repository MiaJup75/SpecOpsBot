import requests
import sqlite3
import datetime

# Dexscreener endpoint for new Solana pairs
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"

# SQLite DB setup
def ensure_db():
    conn = sqlite3.connect("scanner_cache.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS scanned_tokens (address TEXT PRIMARY KEY, timestamp TEXT)")
    conn.commit()
    conn.close()

def already_scanned(address: str) -> bool:
    conn = sqlite3.connect("scanner_cache.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM scanned_tokens WHERE address = ?", (address,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_scanned(address: str):
    conn = sqlite3.connect("scanner_cache.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO scanned_tokens (address, timestamp) VALUES (?, ?)", (address, str(datetime.datetime.now())))
    conn.commit()
    conn.close()

# Honeypot / Backdoor Risk Checker (Mocked logic for now)
def analyze_contract(pair):
    risk_notes = []

    # Fake backdoor triggers (future: use real API)
    token_name = pair.get("baseToken", {}).get("name", "").lower()
    if "fee" in token_name or "rug" in token_name:
        risk_notes.append("setFeesUnlimited")
    if "mint" in token_name or "dev" in token_name:
        risk_notes.append("mintOwner")

    return "✅ Safe" if not risk_notes else f"❌ Risk: {', '.join(risk_notes)}"

# Launch Ping Core
def scan_new_tokens(bot):
    try:
        ensure_db()
        res = requests.get(DEXSCREENER_URL, timeout=5)
        data = res.json()
        pairs = data.get("pairs", [])

        for p in pairs[:20]:
            address = p.get("pairAddress")
            if already_scanned(address):
                continue

            # LP + Age filters
            lp = float(p.get("liquidity", {}).get("usd", 0))
            created = int(p.get("pairCreatedAt", 0))
            age_min = (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(created / 1000)).total_seconds() / 60

            if lp < 10000 or age_min > 30:
                continue

            # Risk scan
            honeypot_result = analyze_contract(p)

            # Format message
            msg = f"""<b>🚀 New Token Launch Detected</b>

<b>Name:</b> {p.get("baseToken", {}).get("symbol", "")}
<b>LP:</b> ${lp:,.0f}
<b>Age:</b> {int(age_min)} min
<b>Risk:</b> {honeypot_result}

🔗 <a href="https://dexscreener.com/solana/{address}">View on Dexscreener</a>
"""
            bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")
            mark_scanned(address)

    except Exception as e:
        print(f"[Scanner Error] {e}")
