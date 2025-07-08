from playwright.sync_api import sync_playwright
from datetime import datetime
import google_sheets  # assumes you have this module ready like in your Economic Times script
import time
URL = ["https://chartink.com/screener/copy-copy-copy-sreelakshmi-guruvayoorappan-b-atr-volume-rocket-8",
       "https://chartink.com/screener/hammar-cash-low-paradaily",
       "https://chartink.com/screener/copy-nk-sir-s-uptrend-stocks-all-time-uptrend",
       "https://chartink.com/screener/agp-bullish2-p5",
       "https://chartink.com/screener/1-longtrend-ve",
       "https://chartink.com/screener/copy-copy-down-tranding-buy-at-low-7",
       "https://chartink.com/screener/copy-akshat-monthly-momentum-37",
       "https://chartink.com/screener/agp-shesha-bulloong1"]
sheet_id = "1NscvYkls78jH3-t28grkSoKJTmWQvdPSulHXgAYFjwg"
worksheet_name = ["p1","p2","p3","p4","p5","p6","p7","p8"]

def scrape_chartink(URL, worksheet_name):
    print(f"🚀 Starting Chartink scrape for {worksheet_name}...")
    print(f"🌐 Loading: {URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(URL)

        print("📊 Waiting for table to load...")
        page.wait_for_selector("table.table-striped.scan_results_table tbody tr", timeout=15000)
        time.sleep(3)  # allow time for AJAX rows to load

        page.screenshot(path=f"{worksheet_name}_debug.png", full_page=True)

        table_rows = page.query_selector_all("table.table-striped.scan_results_table tbody tr")
        print(f"📥 Extracted {len(table_rows)} rows. Updating Google Sheet...")

        headers = ["Sr", "Stock Name", "Symbol", "Links", "Change", "Price", "Volume"]
        rows = []
        for row in table_rows:
            cells = row.query_selector_all("td")
            row_data = [cell.inner_text().strip() for cell in cells]
            rows.append(row_data)

        # Update Sheet
        google_sheets.update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows)

        # Add Timestamp
        now = datetime.now().strftime("Last updated on: %Y-%m-%d %H:%M:%S")
        google_sheets.append_footer(sheet_id, worksheet_name, [now])

        browser.close()
        print(f"✅ Google Sheet '{worksheet_name}' updated.")


for i in URL:
    scrape_chartink(i,worksheet_name[URL.index(i)])
    print(worksheet_name[URL.index(i)]," updated")

