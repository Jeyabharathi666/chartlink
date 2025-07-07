import json
import os
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
import gspread
import backoff as BackoffClient

from concurrent.futures import ThreadPoolExecutor, wait

Charting_Link = "https://chartink.com/screener/"
Charting_url = 'https://chartink.com/screener/1-longtrend-ve'

spreadsheet_name = "SUN1"
worksheet_letter = "p"
total_no_of_worksheet = 29

scope = [
  'https://www.googleapis.com/auth/spreadsheets',
  "https://www.googleapis.com/auth/drive.file",
  "https://www.googleapis.com/auth/drive"
]

google_credentials_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
google_credentials_dict = json.loads(google_credentials_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_credentials_dict, scope
)

client = gspread.authorize(creds)

with open(file="conditions.txt", mode="r") as file:
  conditions = file.readlines()
total_conditions = len(conditions)
print(f"total conditions: {total_conditions}")

def GetDataFromChartink(payload, worksheet_no):

  payload = {'scan_clause': payload}

  with requests.Session() as s:
    r = s.get(Charting_Link)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf = soup.select_one("[name='csrf-token']")['content']
    s.headers['x-csrf-token'] = csrf
    r = s.post(Charting_url, data=payload)

    df = pd.DataFrame()

    for item in r.json()['data']:
      df = pd.concat([df, pd.DataFrame([item])], ignore_index=True)
  if len(df.index) != 0:
    update_sheet(worksheet_no, df)
  else:
    update_sheet_error(worksheet_no)

def create_worksheet():
  sh = client.create(spreadsheet_name)
  for i in range(1, total_no_of_worksheet):
    letter = f"{worksheet_letter}{i}"
    print(letter)
    sheshadri1_test = sh.add_worksheet(letter, rows=100, cols=100)
  print("[+] succesfully created the worksheet...")

def update_sheet(worksheet, data):
  data = data.sort_values(by='per_chg', ascending=False)
  print(data)
  print(
    "--------------------------------------------------------------------------------------"
  )
  #sheshadri1_test = client.open(spreadsheet_name).add_worksheet("r1", rows=100, cols=100)
  sheshadri1_test = client.open(spreadsheet_name).worksheet(worksheet)
  sheshadri1_test.clear()
  sheshadri1_test.update([data.columns.values.tolist()] + data.values.tolist())
  sheshadri1_test.format('A1:G1', {'textFormat': {'bold': True}})

def update_sheet_error(worksheet):
  print(f"[-] Update Sheet {worksheet} error")
  sheshadri1_test = client.open(spreadsheet_name).worksheet(worksheet)
  sheshadri1_test.clear()
  sheshadri1_test.update_cell(1, 1, "no data")


with ThreadPoolExecutor() as executor:
  futures = [ executor.submit(GetDataFromChartink, f"{conditions[i]}", f"p{i+1}") for i in range(total_conditions)]
  print("[+] Getting data from chart link please wait...")
  wait(futures)
  print("[+] Successfully Updated the Data to sheet")
