import gspread
from google.oauth2.service_account import Credentials
import os
import json

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# def get_client():
#     """Authenticate and return a gspread client"""
#     creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
#     return gspread.authorize(creds)

def get_client():
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    return gspread.authorize(creds)


def write_results_to_sheet(spreadsheet_name: str, keyword: str, results: list):
    """Write SERP results with entity counts to Google Sheets"""
    client = get_client()

    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)

    # --- Sheet 1: Main results ---
    try:
        sheet1 = spreadsheet.worksheet("搜尋結果")
    except gspread.WorksheetNotFound:
        sheet1 = spreadsheet.add_worksheet("搜尋結果", 100, 10)

    sheet1.clear()
    sheet1.append_row(["排名", "標題", "網址", "Entity總數"])

    for i, r in enumerate(results, 1):
        sheet1.append_row([
            i,
            r.get("title", ""),
            r.get("link", ""),
            r.get("entity_count", 0)
        ])

    # --- Sheet 2: Entity clustering ---
    try:
        sheet2 = spreadsheet.worksheet("Entity分群")
    except gspread.WorksheetNotFound:
        sheet2 = spreadsheet.add_worksheet("Entity分群", 100, 10)

    sheet2.clear()
    sheet2.append_row(["Entity類型", "數量"])

    # Merge all entity clusters from all articles
    merged_clusters = {}
    for r in results:
        for label, count in r.get("entity_clusters", {}).items():
            merged_clusters[label] = merged_clusters.get(label, 0) + count

    for label, count in merged_clusters.items():
        sheet2.append_row([label, count])

    print(f"✅ Written to Google Sheets: {spreadsheet_name}")
    print(f"🔗 Sheet URL: {spreadsheet.url}")