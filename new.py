import os
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Google Sheet config
spreadsheet_name = "BusinessStandard"
worksheet_name = "reports"

# Auth
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

google_credentials_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')  # for GitHub Actions
google_credentials_dict = json.loads(google_credentials_json)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_credentials_dict, scope)
client = gspread.authorize(creds)

def parse_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    cards = soup.select(".listing-txt")

    data = []

    for card in cards:
        try:
            title = card.select_one("h2 a").get_text(strip=True)
            summary = card.select_one("p").get_text(strip=True)
            date = card.select_one(".date").get_text(strip=True)
            data.append({
                "Date": date,
                "Title": title,
                "Summary": summary
            })
        except Exception as e:
            print("Parse error:", e)

    return pd.DataFrame(data)

def fetch_ajax_html(offset, page, timeout=8000):
    ajax_html = None

    def handle_response(response):
        nonlocal ajax_html
        if "bs_marketresearchreport_list_ajax" in response.url and f"offset={offset}" in response.url:
            if response.status == 200:
                ajax_html = response.text()

    page.on("response", handle_response)

    url = f"https://www.business-standard.com/markets/research-report"
    print(f"Loading offset {offset}...")
    page.goto(url)
    page.wait_for_timeout(2000)
    page.evaluate(f"window.scrollTo(0, {offset * 300})")
    page.wait_for_timeout(timeout)

    return ajax_html

def scrape_all_pages():
    all_data = pd.DataFrame()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for offset in [0, 10, 20]:  # Add more offsets as needed
            html = fetch_ajax_html(offset, page)
            if html:
                df = parse_html(html)
                all_data = pd.concat([all_data, df], ignore_index=True)
            else:
                print(f"No data for offset {offset}")

        browser.close()
    return all_data

def update_sheet(df):
    if df.empty:
        print("No data to update.")
        return

    df = df.sort_values(by="Date", ascending=False)

    try:
        sheet = client.open(spreadsheet_name).worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open(spreadsheet_name).add_worksheet(title=worksheet_name, rows="100", cols="20")

    sheet.clear()
    sheet.update([df.columns.tolist()] + df.values.tolist())
    print("✅ Google Sheet updated.")

if __name__ == "__main__":
    print("🚀 Scraping Business Standard Reports...")
    data = scrape_all_pages()
    update_sheet(data)
