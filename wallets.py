from db import get_wallets

def format_wallet_summary() -> str:
    wallets = get_wallets()
    if not wallets:
        return "No wallets currently tracked."
    
    lines = []
    for label, address in wallets:
        lines.append(f"• <b>{label}</b>\n<code>{address}</code>")
    
    return "\n\n".join(lines)
