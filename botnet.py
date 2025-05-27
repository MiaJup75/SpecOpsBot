import os
import datetime
import random

def detect_botnet_activity(bot):
    try:
        # Simulated suspicious behavior (real logic would parse raw tx logs)
        fake_buys = random.randint(5, 12)
        pattern_size = random.choice([0.22, 0.33, 0.69])
        copy_delay = random.choice(["<10s", "<5s", "identical timing"])
        token = random.choice(["MAX", "ZAZA", "WEN", "RUGME"])

        msg = f"""<b>🤖 Botnet Activity Detected</b>

Token: ${token}  
🔁 <b>{fake_buys} identical buys</b> at {pattern_size} SOL  
⏱ Pattern delay: {copy_delay}  
📛 Potential spam bot swarm or fake launch pump

<i>Timestamp: {datetime.datetime.now().strftime('%H:%M:%S')}</i>
"""
        bot.send_message(chat_id=os.getenv("CHAT_ID"), text=msg, parse_mode="HTML")

    except Exception as e:
        print(f"[Botnet Alert Error] {e}")
