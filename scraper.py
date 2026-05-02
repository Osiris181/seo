import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_serp_results(keyword: str):
    """Fetch top 10 Google results for a keyword using SerpAPI"""
    params = {
        "q": keyword,
        "hl": "zh-tw",
        "gl": "tw",
        "api_key": SERPAPI_KEY,
        "num": 10
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    results = []
    for r in data.get("organic_results", [])[:10]:
        results.append({
            "title": r.get("title", ""),
            "link": r.get("link", ""),
            "snippet": r.get("snippet", "")
        })
    return results


def get_article_text(url: str):
    """Scrape plain text from an article URL"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # Remove scripts and style tags
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""