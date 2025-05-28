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
}

def get_token_config(symbol: str) -> dict | None:
    return TOKEN_CONFIG.get(symbol.upper())

def add_or_update_token(symbol: str, pair: str, mint: str, target_price: float, description: str = ""):
    TOKEN_CONFIG[symbol.upper()] = {
        "pair": pair,
        "mint": mint,
        "target_price": target_price,
        "description": description,
    }

def remove_token(symbol: str) -> bool:
    return TOKEN_CONFIG.pop(symbol.upper(), None) is not None

def list_all_tokens() -> list[str]:
    return list(TOKEN_CONFIG.keys())
