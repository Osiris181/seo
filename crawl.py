import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY")

def search_google(keyword):
    params = {
        "q": keyword,
        "hl": "zh-tw",
        "gl": "tw",
        "api_key": API_KEY,
        "num": 10
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    
    results = []
    for r in data.get("organic_results", [])[:10]:
        results.append({
            "title": r.get("title"),
            "link": r.get("link"),
            "snippet": r.get("snippet")
        })
    return results

keyword = input("請輸入關鍵字: ") 
results = search_google(keyword)