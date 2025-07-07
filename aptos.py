import requests


# 替换为你要查询的 Aptos 地址
APTOS_ADDRESS = "0x53ce075d21ea0ef4b9a44b623aae586af41963142483f83310397ab6d35dc83f"

# CoinGecko 支持的币符映射（可根据实际需求扩展）
COINGECKO_IDS = {
    "aptos": "aptos",
    "usdt": "tether",
    "usdc": "usd-coin",
    "btc": "bitcoin",
    "eth": "ethereum",
    "xbtc": "bitcoin",
    "wrappedxbtc": "bitcoin" 
    # 可扩展其他币9
}

def get_aptos_resources(address):
    url = f"https://fullnode.mainnet.aptoslabs.com/v1/accounts/{address}/resources"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def extract_coin_balances(resources):
    coin_balances = {}
    for res in resources:
        if res["type"].startswith("0x1::coin::CoinStore"):
            coin_type = res["type"].split("<")[1].split(">")[0]
            balance = int(res["data"]["coin"]["value"]) / (10 ** 8)  # 默认按 8 位精度处理，APT是8位，小币种需单独适配
            coin_balances[coin_type] = balance
    return coin_balances

def normalize_coin_symbol(coin_type):
    # 简化 coin type，例如 0x1::aptos_coin::AptosCoin => aptos
    if "aptos_coin::AptosCoin" in coin_type:
        return "aptos"
    elif "::usdc" in coin_type.lower():
        return "usdc"
    elif "::usdt" in coin_type.lower():
        return "usdt"
    elif "::btc" in coin_type.lower():
        return "btc"
    elif "::eth" in coin_type.lower():
        return "eth"
    else:
        return coin_type.lower().split("::")[-1]

def get_usd_prices(symbols):
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(COINGECKO_IDS[s] for s in symbols if s in COINGECKO_IDS),
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    prices = response.json()
    print(prices)
    return {symbol: prices.get(COINGECKO_IDS[symbol], {}).get("usd", 0) for symbol in symbols}

def main():
    resources = get_aptos_resources(APTOS_ADDRESS)
    coin_balances = extract_coin_balances(resources)

    # 映射 coinType 为常见 symbol
    symbol_balances = {}
    for coin_type, balance in coin_balances.items():
        symbol = normalize_coin_symbol(coin_type)
        symbol_balances[symbol] = symbol_balances.get(symbol, 0) + balance

    usd_prices = get_usd_prices(symbol_balances.keys())

    print("资产明细（美元）：")
    total_usd = 0
    for symbol, amount in symbol_balances.items():
        usd_value = amount * usd_prices.get(symbol, 0)
        total_usd += usd_value
        print(f"{symbol.upper()}: {amount:.4f} ≈ ${usd_value:.2f}")

    print(f"\n总资产（USD）: ${total_usd:.2f}")

if __name__ == "__main__":
    main()