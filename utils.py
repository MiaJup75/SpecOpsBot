# utils.py – Token Stat Fetcher, Wallet SPL Parser, Formatting Tools

import requests
import base58
import time
from collections import defaultdict

cooldowns = defaultdict(float)

def get_spl_tokens_from_wallet(wallet_address, min_balance=1):
    try:
        url = f"https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet_address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        token_accounts = response.json().get("result", {}).get("value", [])
        tokens = []
        for acc in token_accounts:
            info = acc["account"]["data"]["parsed"]["info"]
            amount = int(info["tokenAmount"]["amount"])
            decimals = int(info["tokenAmount"]["decimals"])
            ui_amount = amount / (10 ** decimals) if decimals > 0 else amount
            if ui_amount >= min_balance:
                tokens.append({
                    "symbol": info.get("mint")[:6],  # Temp symbol fallback
                    "address": info.get("mint"),
                    "balance": ui_amount
                })
        return tokens
    except Exception:
        return []

def get_token_stats(token_address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token_address}"
    r = requests.get(url, timeout=10)
    data = r.json()

    pair = data.get("pair")
    if not pair:
        raise ValueError("Token not found")

    return {
        "symbol": pair.get("baseToken", {}).get("symbol", ""),
        "priceUsd": float(pair.get("priceUsd", 0)),
        "marketCap": float(pair.get("fdv", 0)),
        "volume24h": float(pair.get("volume", 0)),
        "liquidity": float(pair.get("liquidity", {}).get("usd", 0)),
        "txns": pair.get("txns", {}),
        "createdAt": pair.get("pairCreatedAt"),
        "dex": pair.get("dexId"),
        "url": f"https://dexscreener.com/solana/{token_address}"
    }

def format_token_stats(stats, label=None):
    buys = stats["txns"].get("buys", "?")
    sells = stats["txns"].get("sells", "?")
    launch = time.strftime('%Y-%m-%d', time.gmtime(stats["createdAt"] // 1000)) if stats["createdAt"] else "N/A"

    return (
        f"<b>{stats['symbol']}</b> — <code>${stats['priceUsd']:.5f}</code>\n"
        f"📊 MC: ${int(stats['marketCap']):,} | 24h Vol: ${int(stats['volume24h']):,}\n"
        f"💧 LP: ${int(stats['liquidity']):,} | 📈 {buys} Buys / {sells} Sells\n"
        f"📅 Launch: {launch} | 🔗 <a href='{stats['url']}'>View</a>"
    )

def get_trending_coins(limit=10):
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        r = requests.get(url, timeout=10)
        pairs = r.json().get("pairs", [])
        trending = []
        for p in pairs[:limit]:
            symbol = p.get("baseToken", {}).get("symbol", "???")
            price = float(p.get("priceUsd", 0))
            vol = int(p.get("volume", 0))
            url = f"https://dexscreener.com/solana/{p.get('pairAddress')}"
            trending.append(f"<b>{symbol}</b> - ${price:.5f} | Vol: ${vol:,} | <a href='{url}'>Chart</a>")
        return "<b>🔥 Top 10 Trending Solana Tokens</b>\n\n" + "\n".join(trending)
    except Exception:
        return "⚠️ Could not fetch trending coins."
