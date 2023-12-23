import requests

token = "POPCAT"

def fetch_data(token):
   
    url = "https://api.dexscreener.com/latest/dex/search/?q=:"+token+"%20USD"
    response = requests.get(url)
    return response.json()

response = fetch_data(token)
print(response)

def get_price_usd(pair_data, token):
    return float(pair_data['priceUsd'])

# Iterate through each pair and print the current price in USD
for pair in response['pairs']:
    base_token_name = pair['baseToken']['name']
    quote_token_name = pair['quoteToken']['name']
    address = pair['pairAddress']
    chain_id = pair['chainId']
    percentage_5m = pair['priceChange']['m5']
    percentage_1h = pair['priceChange']['h1']
    percentage_6h = pair['priceChange']['h6']
    percentage_24h = pair['priceChange']['h24']
    market_cap = pair['fdv']
    price_usd = get_price_usd(pair, token)

    chart_link = f"https://dexscreener.com/{chain_id}/{address}"

        
    if base_token_name.lower() == token.lower():
        #print(f"{base_token_name}/{quote_token_name} Price: ${price_usd:.5f}")
        print(f"{base_token_name}/{quote_token_name} Price: ${price_usd:.5f} 5m: {percentage_5m:.2f}% 1h: {percentage_1h:.2f}% 6h: {percentage_6h:.2f}% 24h: {percentage_24h:.2f}% Market Cap: ${market_cap:.2f}")
        print(f"Chart: {chart_link}")