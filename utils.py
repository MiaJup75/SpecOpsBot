import requests
import json
import time
import random
import logging
from datetime import datetime
from config import config

MAX_TOKEN_ADDRESS = config["max_token"]
DEXSCREENER_API = f"https://api.dexscreener.io/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"

def fetch_max_token_data():
    try:
        res = requests.get(DEXSCREENER_API)
        data = res.json()["pairs"][0]

        price = float(data["priceUsd"])
        market_cap = round(data["marketCap"])
        volume = float(data["volume"]["h24"])
        fdv = round(data["fdv"])
        txns = data["txns"]["h24"]
        liquidity = round(data["liquidity"]["usd"], 2)
        change = round(data["priceChange"]["h24"], 2)
        launch_timestamp = int(data["pairCreatedAt"]) // 1000

        launch_time = datetime.utcfromtimestamp(launch_timestamp).strftime('%Y-%m-%d %H:%M UTC')

        return {
            "price": price,
            "market_cap": market_cap,
            "volume": volume,
            "fdv": fdv,
            "buys": txns["buys"],
            "sells": txns["sells"],
            "liquidity": liquidity,
            "change": change,
            "launch_time": launch_time,
        }
    except Exception as e:
        logging.error(f"Error fetching MAX data: {e}")
        return None

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]

def get_trending_coins():
    # Dummy data placeholder – integrate actual Birdeye/Dexscreener API
    return [
        {"name": "DOGE420", "price": "0.00000230", "volume": "$432,112"},
        {"name": "FROGZILLA", "price": "0.00000944", "volume": "$210,000"},
        {"name": "PEPEC", "price": "0.00000033", "volume": "$109,870"},
        {"name": "LUNAR", "price": "0.00421", "volume": "$81,450"},
        {"name": "BONGCAT", "price": "0.000882", "volume": "$71,110"},
    ]

def fetch_new_tokens():
    # Simulated data – should fetch from Birdeye API (12h window)
    return [
        {"name": "STEALTHCOIN", "age": "4h", "liquidity": "$7,000"},
        {"name": "RAIDPEPE", "age": "2h", "liquidity": "$13,000"},
    ]

def check_suspicious_activity():
    # Simulated detection
    return [
        "⚠️ Whale dumped 1.2M MAX",
        "⚠️ Dev wallet removed 20% LP"
    ]

def summarize_wallet_activity():
    # Simulated data
    return {
        "wallets": [
            {"name": "Main Wallet", "activity": "+3 buys / 1 sell"},
            {"name": "Trojan Wallet", "activity": "Idle"},
        ]
    }

def classify_narratives():
    return [
        {"theme": "Dogs", "tokens": ["MAX", "DOGE420", "SHIBAETH"]},
        {"theme": "Memes", "tokens": ["PEPE", "BONGCAT"]},
    ]

def send_target_alerts():
    # Simulated alerting
    return ["🎯 $MAX hit target zone – consider partial exit."]
