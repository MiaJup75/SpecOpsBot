def fetch_max_token_data():
    return 0.0003382, 338157, 1449, 338157

def get_trending_coins():
    return [
        {"name": "SOL", "price": "177.94", "volume": 104107},
        {"name": "SOL", "price": "0.00028340", "volume": 1202},
        {"name": "SOL", "price": "177.75", "volume": 1618010},
        {"name": "SOL", "price": "177.61", "volume": 330633},
        {"name": "SOL", "price": "177.83", "volume": 47040}
    ]

def get_new_tokens():
    return []

def get_alerts():
    return []

def get_wallet_activity():
    return []

def is_allowed(user_id):
    return str(user_id) in ["7623873892"]