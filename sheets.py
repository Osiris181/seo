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
    client = get_client()

    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)

    # --- Tab 1: Per article results with actual entity terms ---
    try:
        sheet1 = spreadsheet.worksheet("搜尋結果")
    except gspread.WorksheetNotFound:
        sheet1 = spreadsheet.add_worksheet("搜尋結果", 100, 10)

    sheet1.clear()
    sheet1.append_row(["排名", "標題", "網址", "Entity數量", "Entity詞彙"])

    # 1. Create a list to hold all rows for Tab 1
    tab1_data = []
    for i, r in enumerate(results, 1):
        entity_terms = ", ".join([text for text, label in r.get("entities", [])])
        tab1_data.append([
            i,
            r.get("title", ""),
            r.get("link", ""),
            r.get("entity_count", 0),
            entity_terms
        ])
        
    # 2. Send all Tab 1 data in ONE API call
    if tab1_data:
        sheet1.append_rows(tab1_data)

    # --- Tab 2: Entity clusters with actual terms and counts ---
    try:
        sheet2 = spreadsheet.worksheet("Entity分群")
    except gspread.WorksheetNotFound:
        sheet2 = spreadsheet.add_worksheet("Entity分群", 100, 10)

    sheet2.clear()
    sheet2.append_row(["Entity類型", "詞彙", "出現次數"])

    from collections import Counter
    term_label_counts = Counter()
    for r in results:
        for text, label in r.get("entities", []):
            term_label_counts[(label, text)] += 1

    # 3. Create a list to hold all rows for Tab 2
    tab2_data = []
    for (label, text), count in term_label_counts.most_common():
        tab2_data.append([label, text, count])

    # 4. Send all Tab 2 data in ONE API call
    if tab2_data:
        sheet2.append_rows(tab2_data)

    print(f"✅ Written to Google Sheets: {spreadsheet_name}")