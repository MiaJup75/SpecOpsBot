# mirror.py – Mirror Wallet Tracking & Sync

from db import get_wallets

def get_mirror_wallets():
    wallets = get_wallets()
    mirror_wallets = [addr for label, addr in wallets if label.lower().startswith("mirror")]
    return mirror_wallets

def get_friend_wallets():
    wallets = get_wallets()
    friend_wallets = [addr for label, addr in wallets if label.lower().startswith("friend")]
    return friend_wallets
