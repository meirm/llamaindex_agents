import yfinance as yf

def get_forex_exchange_rates(pairs: list):
    """Fetches Forex exchange rates using Yahoo Finance.
    
    Args:
        pairs (list): A list of currency pairs to fetch exchange rates for (e.g., ['EURUSD=X', 'GBPUSD=X']).
    
    Returns:
        dict: A dictionary containing exchange rates.
    """
    data = yf.download(pairs, period='1d', interval='1d')
    exchange_rates = {}
    print(type(pairs))
    print(pairs)
    for pair in pairs:
        try:
            if len(pairs) == 1:
                exchange_rates[pair] = data['Close'].iloc[-1]
            else:
                exchange_rates[pair] = data['Close'][pair].iloc[-1]
        except KeyError:
            exchange_rates[pair] = 'Data not available'
    
    return exchange_rates

def display_exchange_rates(rates):
    """Displays Forex exchange rates.
    
    Args:
        rates (dict): A dictionary containing exchange rates.
    """
    print("Forex Exchange Rates:")
    for pair, rate in rates.items():
        print(f"{pair}: {rate}")

# Sample usage
currency_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDEUR=X']
exchange_rates = get_forex_exchange_rates(currency_pairs)
display_exchange_rates(exchange_rates)
