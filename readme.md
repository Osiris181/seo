# 4G吃到飽 SEO Analyzer

A tool that crawls Google's first page for any keyword, extracts entities from each article, and saves the results to Google Sheets and Supabase.

## Live Demo
🔗 [Vercel URL](https://seo-analyzer-ndkdidkhf-osiris181s-projects.vercel.app/docs)

## Login
| Field | Value |
|---|---|
| Username | admin |
| Password | password123 |

## How to Use
1. Go to the live URL
2. Enter your username and password
3. Add your keyword to the URL:
```
/analyze?keyword=4G吃到飽
```
4. Or just straight up click analyze, Try it out, and then input the keyword 4G吃到飽

## What it Does
- Crawls Google top 10 results for any keyword using SerpAPI
- Extracts named entities from each article using Google Cloud NLP
- Saves results and entity clusters to Google Sheets
- Stores all data in Supabase

## Results
- 📊 [Google Sheet](https://docs.google.com/spreadsheets/d/1TObHOmW488_bWkgn0tXGDZKW9cvLUrOtcMleyGxO0_k/edit?usp=sharing)
- 🗄️ Data stored in Supabase table `serp_results`

## Tech Stack
- **FastAPI** — backend API
- **SerpAPI** — Google search results
- **Google Cloud NLP** — entity extraction
- **gspread** — Google Sheets integration
- **Supabase** — database storage
- **Vercel** — deployment

## Project Structure
```
├── main.py        # FastAPI controller
├── scraper.py     # SerpAPI + article scraping
├── entities.py    # Entity extraction
├── sheets.py      # Google Sheets output
├── database.py    # Supabase storage
├── auth.py        # Login authentication
├── chart.py       # Entity cluster chart
└── requirements.txt
```

## Local Setup
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```