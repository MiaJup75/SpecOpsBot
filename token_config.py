# Token configuration for your bot - mint addresses, pair IDs, price targets, etc.

TOKEN_CONFIG = {
    "MAX": {
        "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
        "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
        "target_price": 0.00005
    },
    "BONK": {
        "pair": "examplepairaddressbonk",
        "mint": "examplemintaddressbonk",
        "target_price": 0.00002
    },
    "MEOW": {
        "pair": "examplepairaddressmeow",
        "mint": "examplemintaddressmeow",
        "target_price": 0.00001
    }
    # Add more tokens as you track them
}

def get_token_config(symbol: str):
    return TOKEN_CONFIG.get(symbol.upper())
