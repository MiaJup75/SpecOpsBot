import requests
import datetime
import os

# Dexscreener Solana endpoint
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"

def scan_stealth_tokens(bot):
    try:
        res = requests.get(DEXSCREENER_URL, timeout=5)
        data = res.json()
        pairs = data.get("pairs", [])[:20]

        for p in pairs:
            lp = float(p.get("liquidity", {}).get("usd", 0))
            created = int(p.get("pairCreatedAt", 0))
            age_min = (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(created / 1000)).total_seconds() / 60

            socials = p.get("info", {})
            has_socials = any(socials.get(key) for key in ["telegram", "twitter", "website"])

            if lp > 5000 and age_min < 30 and not has_socials:
                symbol = p.get("baseToken", {}).get("symbol", "???")
                name = p.get("baseToken", {}).get("name", "Unknown")
                address = p.get("pairAddress", "")
                msg = f"""<b>🕵️ Stealth Token Spotted</b>

<b>Name:</b> {name} (${symbol})
<b>LP:</b> ${lp:,.0f}
<b>Age:</b> {int(age_min)} min
<b>Socials:</b> ❌ None

🔗 <a href="https://dexscreener.com/solana/{address}">View on Dexscreener</a>
"""
                bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")

    except Exception as e:
        print(f"[Stealth Scanner Error] {e}")
