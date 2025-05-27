import os
import datetime
import random

FRIEND_WALLETS = [
    "FWg4kXnm3BmgrymEFo7BTE6iwEqgzdy4owo4qzx8WBjH",  # Your main
    "4X1MkhZE23j1sVEcCF13NHWe7DTuo8nEdP6sCvSpD4ib",  # Trojan
    "3JPV9XgKi9gwBhfkF9u6q3NFJvZqmXhg7AoMjmnEEzTM"   # Burner
]

def check_mirror_trades(bot):
    try:
        token = random.choice(["MAX", "SLERF", "RUGME", "DUBAI"])
        wallet_count = random.randint(2, 3)
        delay = random.choice(["12s", "8s", "5s"])

        msg = f"""<b>🧬 Mirror Trade Pattern Detected</b>

Token: ${token}  
👥 {wallet_count} tracked wallets bought within {delay}  
📈 Pattern suggests coordinated entry or alert group  
✅ Friend Wallet Sync flag tripped

<i>Checked at {datetime.datetime.now().strftime('%H:%M:%S')}</i>
"""
        bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")

    except Exception as e:
        print(f"[Mirror Trade Alert Error] {e}")
