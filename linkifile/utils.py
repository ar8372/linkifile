from time import sleep
from bs4 import BeautifulSoup
import requests
import urllib
import random
import pandas as pd

def get_useragent():
    return random.choice(_useragent_list)

_useragent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
]

def _req(term, results, lang, start, proxies, timeout):
    resp = None
    try:
        resp = requests.get(
            url="https://www.google.com/search",
            headers={
                "User-Agent": get_useragent()
            },
            params={
                "q": term,
                "num": results + 2,  # Prevents multiple requests
                "hl": lang,
                "start": start,
            },
            proxies=proxies,
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("Too Many Requests (429) Error: You've exceeded the rate limit.")
        else:
            print(f"HTTP Error {e.response.status_code}: {e.response.reason}")
        resp = None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        resp = None
    return resp

def parse_query(term, query):
    # term: "Areva"
    # query: "{{x}} industry official website"
    return query.replace("{{x}}", term)

def load_data(file_path, file_type):
    if file_type == "csv":
        return pd.read_csv(file_path)
    elif file_type == "xlsx":
        return pd.read_excel(file_path)
    
def save_data(df, file_path, file_type):
    if file_type == "csv":
        return df.to_csv(file_path, index=False)
    elif file_type == "xlsx":
        return df.to_excel(file_path, index=False)

class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"

def search(term, query=None, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5):
    """Search the Google search engine
    Note: this function is a modified version of googlesearch package"""
    if query is not None:
        term = parse_query(term, query)
    escaped_term = urllib.parse.quote_plus(term) # make 'site:xxx.xxx.xxx ' works.

    # Proxy
    proxies = None
    if proxy:
        if proxy.startswith("https"):
            proxies = {"https": proxy}
        else:
            proxies = {"http": proxy}

    # Fetch
    start = 0
    while start < num_results:
        # Send request
        resp = _req(escaped_term, num_results - start,
                    lang, start, proxies, timeout)
        if resp is None:
            yield ""
            return  

        # Parse
        soup = BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", attrs={"class": "g"})
        if len(result_block) ==0:
            start += 1
        for result in result_block:
            # Find link, title, description
            link = result.find("a", href=True)
            title = result.find("h3")
            description_box = result.find(
                "div", {"style": "-webkit-line-clamp:2"})
            if description_box:
                description = description_box.text
                if link and title and description:
                    start += 1
                    if advanced:
                        yield SearchResult(link["href"], title.text, description)
                    else:
                        yield link["href"]
        sleep(sleep_interval)

        if start == 0:
            yield ""
            return []
