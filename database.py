from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def save_results(keyword: str, results: list):
    """Save SERP analysis results to Supabase"""
    client = get_client()

    for r in results:
        client.table("serp_results").insert({
            "keyword": keyword,
            "title": r.get("title", ""),
            "url": r.get("link", ""),
            "snippet": r.get("snippet", ""),
            "entity_count": r.get("entity_count", 0),
            "entity_clusters": r.get("entity_clusters", {})
        }).execute()

    print(f"✅ Saved {len(results)} results to Supabase")