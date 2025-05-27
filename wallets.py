from db import get_wallets

def format_wallet_summary():
    wallets = get_wallets()
    if not wallets:
        return "No wallets currently tracked."

    lines = ["<b>👛 Tracked Wallets</b>"]
    for label, addr in wallets:
        lines.append(f"• <b>{label}</b>\n<code>{addr}</code>")

    return "\n".join(lines)
