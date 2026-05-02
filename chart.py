import os
import matplotlib
# Use 'Agg' backend for headless server environments like Vercel
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client

# Define the temporary path for Vercel's writable directory
TEMP_CHART_PATH = "/tmp/entity_chart.png"

def get_sheets_client():
    """Authenticates and returns a Google Sheets client."""
    SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Ensure credentials.json is in your root folder
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    return gspread.authorize(creds)

def get_supabase_client():
    """Creates a Supabase client using environment variables."""
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def generate_entity_chart(spreadsheet_name: str):
    """Reads data from Sheets and creates the .png file locally."""
    client = get_sheets_client()
    spreadsheet = client.open(spreadsheet_name)
    sheet = spreadsheet.worksheet("Entity分群")
    data = sheet.get_all_records()

    labels = [row["Entity類型"] for row in data]
    counts = [row["數量"] for row in data]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color="steelblue")
    plt.title("Entity Grouping")
    plt.xlabel("Entity")
    plt.ylabel("Quantity")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save to the only writable folder on Vercel
    plt.savefig(TEMP_CHART_PATH)
    plt.close()
    return TEMP_CHART_PATH

def upload_to_supabase(local_path: str, bucket_name: str = "charts"):
    """Uploads the file to Supabase Storage and returns the public URL."""
    supabase = get_supabase_client()
    file_name = os.path.basename(local_path)

    with open(local_path, "rb") as f:
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=f,
            file_options={
                "content-type": "image/png",
                "x-upsert": "true" # Overwrites existing chart
            }
        )

    url = supabase.storage.from_(bucket_name).get_public_url(file_name)
    
    # Clean up the /tmp file after successful upload
    if os.path.exists(local_path):
        os.remove(local_path)
    
    return url

def run_visualization_pipeline(spreadsheet_name: str):
    """The 'one-call' function to trigger everything."""
    print(f"📊 Starting visualization for {spreadsheet_name}...")
    path = generate_entity_chart(spreadsheet_name)
    public_url = upload_to_supabase(path)
    print(f"✅ Chart live at: {public_url}")
    return public_url