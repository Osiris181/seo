from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse
from scraper import get_serp_results, get_article_text
from entities import extract_entities, count_entities, cluster_entities_by_label
from sheets import write_results_to_sheet
from database import save_results
from auth import verify_login
from chart import run_visualization_pipeline

app = FastAPI()


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/analyze")
async def analyze(
    keyword: str, 
    background_tasks: BackgroundTasks, # Add BackgroundTasks here
    user: str = Depends(verify_login)
):
    """
    Main endpoint — triggers scraping, NLP, Google Sheets, 
    Database saving, and Background Visualization.
    """

    # Step 1: Get top 10 Google results
    results = get_serp_results(keyword)

    # Step 2: Scrape article content + extract entities
    for r in results:
        text = get_article_text(r["link"])
        entities = extract_entities(text)
        r["entity_count"] = count_entities(entities)
        r["entity_clusters"] = cluster_entities_by_label(entities)

    # Step 3: Write to Google Sheets
    spreadsheet_name = "4G吃到飽分析"
    write_results_to_sheet(spreadsheet_name, keyword, results)

    # Step 4: Save to Supabase Database
    save_results(keyword, results)

    # Step 5: Trigger Chart Generation in the Background
    # This runs chart.py logic WITHOUT making the user wait
    background_tasks.add_task(run_visualization_pipeline, spreadsheet_name)

    return {
        "status": "Success",
        "keyword": keyword,
        "total_articles": len(results),
        "message": "Analysis complete. Visualization is processing in the background."
    }