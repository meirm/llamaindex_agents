def add(x: float, y: float) -> float:
    """Adds two floats together."""
    return x + y

def subtract(x: float, y: float) -> float:
    """Subtracts two floats together."""
    return x - y

def multiply(x: float, y: float) -> float:
    """Multiplies two floats together."""
    return x * y

def divide(x: float, y: float) -> float:
    """Divides two floats together."""
    if y == 0:
        raise ValueError("Cannot divide by zero!")
    return x / y

def human_input(query:str) -> str: 
    """Prompts the user for input."""
    return input(query)

import sys
import io

class CodeExecutor:
    def __init__(self):
        pass
    
    def execute_code(self, code):
        try:
            # Redirect stdout to capture print outputs
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            
            # Compile and execute the code
            exec(code)
            
            # Get the output
            output = new_stdout.getvalue()
            print("Output:", output)
            # Restore stdout
            sys.stdout = old_stdout
            
            return output
        except Exception as e:
            return str(e)

# Sample usage
# code_executor = CodeExecutor()
# sample_code = """
# def fibonacci(n):
#     if n <= 1:
#         return n
#     else:
#         return fibonacci(n-1) + fibonacci(n-2)

# result = fibonacci(12)
# print(result)
# """
# output = code_executor.execute_code(sample_code)
# print("Output:", output)

def repl(code:str) -> str:
    """Execute python code and returns the stdout. Code needs to print the output."""
    code_executor = CodeExecutor()
    output = code_executor.execute_code(code)
    print("Output:", output)
    print("Code:", code)
    return output


import wikipediaapi

def get_wikipedia_summary(page_title: str, language: str = 'en') -> str:
    """Fetches the summary from a Wikipedia page.
    
    Args:
        page_title (str): The title of the Wikipedia page.
        language (str): The language of the Wikipedia page (default is 'en' for English).
    
    Returns:
        str: The summary of the Wikipedia page if found, else an error message.
    """
    wiki_wiki = wikipediaapi.Wikipedia(language)
    page = wiki_wiki.page(page_title)

    if page.exists():
        return page.summary
    else:
        return f"The page '{page_title}' does not exist on Wikipedia in the '{language}' language."

def get_wikipedia_page(page_title: str, language: str = 'en') -> str:
    """Fetches the Page from a Wikipedia page.
    
    Args:
        page_title (str): The title of the Wikipedia page.
        language (str): The language of the Wikipedia page (default is 'en' for English).
    
    Returns:
        str: The page of the Wikipedia page if found, else an error message.
    """
    wiki_wiki = wikipediaapi.Wikipedia(language, headers = {'User-Agent': 'MyCoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'})
    page = wiki_wiki.page(page_title)

    if page.exists():
        return page.text
    else:
        return f"The page '{page_title}' does not exist on Wikipedia in the '{language}' language."


import requests
import json

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
        return json.dumps(response.json())
    else:
        return f"Error: Unable to fetch data, received status code {response.status_code}"
    
import yfinance as yf

def get_stock_price(ticker: str):
    """Fetches the stock price of a given ticker symbol.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        float: The current stock price if available, else an error message.
    """
    stock = yf.Ticker(ticker)
    current_price = stock.history(period='1d')['Close'][-1]
    
    return current_price


def get_forex_exchange_rates(pairs: list):
    """Fetches Forex exchange rates using Yahoo Finance.
    
    Args:
        pairs (list): A list of currency pairs to fetch exchange rates for (e.g., ['EURUSD=X', 'GBPUSD=X']).
    
    Returns:
        dict: A dictionary containing exchange rates.
    """
    data = yf.download(pairs, period='1d', interval='1d')
    exchange_rates = {}
    
    for pair in pairs:
        try:
            if len(pairs) == 1:
                exchange_rates[pair] = data['Close'].iloc[-1]
            else:
                exchange_rates[pair] = data['Close'][pair].iloc[-1]
        except KeyError:
            exchange_rates[pair] = 'Data not available'
    
    return exchange_rates
