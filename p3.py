from playwright.sync_api import sync_playwright
from datetime import datetime
import google_sheets  # assumes you have this module ready like in your Economic Times script

URL = ["https://chartink.com/screener/copy-copy-copy-sreelakshmi-guruvayoorappan-b-atr-volume-rocket-8",
       "https://chartink.com/screener/hammar-cash-low-paradaily",
       "https://chartink.com/screener/copy-nk-sir-s-uptrend-stocks-all-time-uptrend",
       "https://chartink.com/screener/agp-bullish2-p5",
       "https://chartink.com/screener/1-longtrend-ve",
       "https://chartink.com/screener/copy-copy-down-tranding-buy-at-low-7",
       "https://chartink.com/screener/copy-akshat-monthly-momentum-37"]
sheet_id = "1NscvYkls78jH3-t28grkSoKJTmWQvdPSulHXgAYFjwg"
worksheet_name = ["p1","p2","p3","p4","p5","p6","p7"]

def scrape_chartink(URL, worksheet_name):
    print(f"🚀 Starting Chartink scrape for {worksheet_name}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"🌐 Loading: {URL}")
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"❌ Failed to load {URL}: {e}")
            browser.close()
            return

        print("📊 Waiting for table to load...")
        try:
            page.wait_for_selector("table.table-striped.scan_results_table", timeout=10000)
        except Exception as e:
            print(f"❌ Table not found for {worksheet_name}: {e}")
            browser.close()
            return

        print("✅ Table found. Scraping rows...")
        table_rows = page.query_selector_all("table.table-striped.scan_results_table tbody tr")
        headers = ["Sr", "Stock Name", "Symbol", "Links", "Change", "Price", "Volume"]

        rows = []
        for row in table_rows:
            cells = row.query_selector_all("td")
            row_data = [cell.inner_text().strip() for cell in cells]
            rows.append(row_data)

        print(f"📥 Extracted {len(rows)} rows. Updating Google Sheet...")

        from datetime import datetime
        now = datetime.now().strftime("Last updated on: %Y-%m-%d %H:%M:%S")

        try:
            google_sheets.update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows)
            google_sheets.append_footer(sheet_id, worksheet_name, [now])
            print(f"✅ Google Sheet '{worksheet_name}' updated.")
        except Exception as e:
            print(f"❌ Sheet update error for {worksheet_name}: {e}")

        browser.close()

for i in URL:
    scrape_chartink(i,worksheet_name[URL.index(i)])
    print(worksheet_name[URL.index(i)]," updated")

