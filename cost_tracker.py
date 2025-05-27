import requests

WALLET = "FWg4kXnm3BmgrymEFo7BTE6iwEqgzdy4owo4qzx8WBjH"
MAX_MINT = "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump"

def get_dynamic_avg_cost():
    url = f"https://public-api.solscan.io/account/splTransfers?account={WALLET}&limit=100&offset=0"
    headers = {"accept": "application/json"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        txs = r.json().get("data", [])

        total_amount = 0
        total_paid = 0  # we'll estimate SOL paid via logs if possible

        for tx in txs:
            if tx["tokenAddress"] != MAX_MINT:
                continue
            if tx["changeAmount"] <= 0:
                continue  # skip outgoing or zero

            # Estimate SOL cost from optional 'lamports' field if present
            ui_amount = tx["changeAmount"] / (10 ** tx["decimals"])
            sol_paid = tx.get("lamports", 0) / 1e9 if "lamports" in tx else None

            if ui_amount and sol_paid:
                total_amount += ui_amount
                total_paid += sol_paid

        if total_amount > 0 and total_paid > 0:
            return round(total_paid / total_amount, 8)

    except Exception as e:
        print(f"[Avg Cost Error] {e}")

    return None  # fallback to static if no data
