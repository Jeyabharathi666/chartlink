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
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']

google_credentials_json = os.getenv('GOOGLE_CREDENTIALS')
google_credentials_dict = json.loads(google_credentials_json)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_credentials_dict, scope)
client = gspread.authorize(creds)

def parse_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    cards = soup.select(".listing-txt")

    records = []

    for card in cards:
        try:
            title = card.select_one("h2 a").get_text(strip=True)
            summary = card.select_one("p").get_text(strip=True)
            date = card.select_one(".date").get_text(strip=True)
            records.append({
                "Date": date,
                "Title": title,
                "Summary": summary
            })
        except Exception as e:
            print("Error parsing:", e)

    return pd.DataFrame(records)

def scrape_via_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        html_fragment = None

        def handle_response(response):
            nonlocal html_fragment
            if "bs_marketresearchreport_list_ajax" in response.url and response.status == 200:
                html_fragment = response.text()

        page.on("response", handle_response)

        page.goto("https://www.business-standard.com/markets/research-report", timeout=60000)
        page.wait_for_timeout(3000)
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(5000)

        if html_fragment:
            df = parse_html(html_fragment)
            browser.close()
            return df
        else:
            print("Failed to capture AJAX response.")
            browser.close()
            return pd.DataFrame()

def update_sheet(dataframe):
    if dataframe.empty:
        print("No data to update.")
        return

    dataframe = dataframe.sort_values(by="Date", ascending=False)

    try:
        sheet = client.open(spreadsheet_name).worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open(spreadsheet_name).add_worksheet(worksheet_name, rows=100, cols=20)

    sheet.clear()
    sheet.update([dataframe.columns.tolist()] + dataframe.values.tolist())
    print("Google Sheet updated.")

if __name__ == "__main__":
    print("Starting scrape...")
    df = scrape_via_playwright()
    update_sheet(df)

  futures = [ executor.submit(GetDataFromChartink, f"{conditions[i]}", f"p{i+1}") for i in range(total_conditions)]
  print("[+] Getting data from chart link please wait...")
  wait(futures)
  print("[+] Successfully Updated the Data to sheet")
