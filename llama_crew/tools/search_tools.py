
from duckduckgo_search import DDGS

def search_ddg(query: str) -> str:
    "Search online and return the results."
    return DDGS(proxy=None).text(query, max_results=3)


if __name__ == "__main__":
    word = "python"
    results = search_ddg(word)
    print(results)