# token_config.py

# Dictionary storing token configurations keyed by token symbol (uppercase)
TOKEN_CONFIG = {
    "MAX": {
        "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
        "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
        "target_price": 0.00005,
        "description": "Optimus Dog Meme Coin",
    },
    "BONK": {
        "pair": "examplepairaddress1",
        "mint": "examplemintaddress1",
        "target_price": 0.000001,
        "description": "Bonk Token",
    },
    "MEOW": {
        "pair": "examplepairaddress2",
        "mint": "examplemintaddress2",
        "target_price": 0.000002,
        "description": "Meow Token",
    },
    # Add more tokens as needed...
}

def get_token_config(symbol: str) -> dict | None:
    """Return the token config dict for the given symbol, or None if not found."""
    return TOKEN_CONFIG.get(symbol.upper())

def add_or_update_token(symbol: str, pair: str, mint: str, target_price: float, description: str = ""):
    """Add a new token or update existing one."""
    TOKEN_CONFIG[symbol.upper()] = {
        "pair": pair,
        "mint": mint,
        "target_price": target_price,
        "description": description,
    }

def remove_token(symbol: str) -> bool:
    """Remove token config by symbol. Returns True if removed, False if not found."""
    return TOKEN_CONFIG.pop(symbol.upper(), None) is not None

def list_all_tokens() -> list[str]:
    """Return list of all token symbols configured."""
    return list(TOKEN_CONFIG.keys())
