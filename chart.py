import os
import tempfile
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client

# 1. Use dynamic paths so it works locally on Windows AND in the cloud on Vercel
TEMP_DIR = tempfile.gettempdir()
TEMP_CHART_PATH = os.path.join(TEMP_DIR, "entity_chart.png")

# 2. Make sure this exact file is committed to your GitHub repo!
FONT_PATH = "TaipeiSansTCBeta-Regular.ttf"

def get_sheets_client():
    """Authenticates using Environment Variables for Vercel security."""
    SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Check if we are using a local file OR a Vercel Environment Variable
    if os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    else:
        # VERCEL DEPLOYMENT MODE: Reads the JSON from your Vercel Environment Variables
        creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
        
    return gspread.authorize(creds)

def get_supabase_client():
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def generate_entity_chart(spreadsheet_name: str):
    client = get_sheets_client()
    spreadsheet = client.open(spreadsheet_name)
    sheet = spreadsheet.worksheet("Entity分群")
    data = sheet.get_all_records()

    labels = [str(row["詞彙"]) for row in data]
    counts = [int(row["出現次數"]) for row in data]

    paired = sorted(zip(counts, labels), reverse=True)[:10]
    counts, labels = zip(*paired)

    # 🔧 FIX: Load the bundled font directly from the file path
    my_font = fm.FontProperties(fname=FONT_PATH)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(labels, counts, color="steelblue")
    ax.invert_yaxis()

    ax.set_title("Top 10 Entity 詞彙", fontproperties=my_font, fontsize=16)
    ax.set_xlabel("出現次數", fontproperties=my_font, fontsize=12)
    ax.set_ylabel("詞彙", fontproperties=my_font, fontsize=12)

    # ✅ Apply font to ALL tick labels to completely prevent Tofu
    for label in ax.get_yticklabels():
        label.set_fontproperties(my_font)
    for label in ax.get_xticklabels():
        label.set_fontproperties(my_font)

    plt.tight_layout()
    plt.savefig(TEMP_CHART_PATH, dpi=150, bbox_inches='tight')
    plt.close()
    
    return TEMP_CHART_PATH

def upload_to_supabase(local_path: str, bucket_name: str = "charts"):
    supabase = get_supabase_client()
    file_name = os.path.basename(local_path)

    with open(local_path, "rb") as f:
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=f,
            file_options={"content-type": "image/png", "x-upsert": "true"}
        )

    url = supabase.storage.from_(bucket_name).get_public_url(file_name)

    if os.path.exists(local_path):
        os.remove(local_path)

    return url

def run_visualization_pipeline(spreadsheet_name: str):
    print(f"📊 Starting visualization for {spreadsheet_name}...")
    path = generate_entity_chart(spreadsheet_name)
    public_url = upload_to_supabase(path)
    print(f"✅ Chart live at: {public_url}")
    return public_url