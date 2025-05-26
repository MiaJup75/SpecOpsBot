# utils.py
def fetch_max_token_data():
    return (
        "🐶 <b>MAX Token Update</b>\n"
        "💰 Price: $0.00033\n"
        "📊 24h Volume: $1.5K\n"
        "📈 FDV: $338K\n"
        "🔍 Dexscreener: https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    )

def is_allowed(user_id):
    return str(user_id) in ["7623873892"]
