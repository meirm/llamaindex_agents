import requests

def get_top_cryptocurrencies(currency='usd', limit=10):
    """Fetches top cryptocurrencies by price, volume, and market cap from CoinGecko.
    
    Args:
        currency (str): The currency to fetch data in (default is 'usd').
        limit (int): The number of top cryptocurrencies to fetch (default is 10).
    
    Returns:
        list: A list of dictionaries containing cryptocurrency data.
    """
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': currency,
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': 'false'
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: Unable to fetch data, received status code {response.status_code}"

def display_cryptocurrency_data(data):
    """Displays cryptocurrency data.
    
    Args:
        data (list): A list of dictionaries containing cryptocurrency data.
    """
    print(f"{'Name':<20} {'Price':<15} {'Volume':<20} {'Market Cap':<20}")
    print("-" * 75)
    for coin in data:
        name = coin['name']
        price = coin['current_price']
        volume = coin['total_volume']
        market_cap = coin['market_cap']
        print(f"{name:<20} {price:<15} {volume:<20} {market_cap:<20}")

# Sample usage
currency = 'usd'
limit = 10
crypto_data = get_top_cryptocurrencies(currency, limit)
if isinstance(crypto_data, list):
    display_cryptocurrency_data(crypto_data)
else:
    print(crypto_data)
