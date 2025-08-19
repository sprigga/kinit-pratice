from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build

# 指定 JSON 憑證檔案路徑
# CREDENTIALS_PATH = "./secrets/bd-app-1426a-009370c6297d.json"
CREDENTIALS_PATH = '/Users/afu/Documents/重要資料/python/正式專案/bd-sales-oa/api/secrets/bd-app-1426a-009370c6297d.json'

# 指定 Google Sheet 的 ID
SPREADSHEET_ID = "1TlPdkpqdKedZZTCjLLkiXGs6Pv_0UtWANCxLi-gdZHI"

# 指定要讀取的範圍
RANGE_NAME = "表單回應 2!A1:M100"

def normalize_timestamp(ts: str) -> str:
    # 將「上午」與「下午」替換為英文格式 AM / PM
    ts = ts.strip().replace("上午", "AM").replace("下午", "PM")

    formats = ["%Y/%m/%d %p %I:%M:%S", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(ts, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    print(f"❌ 時間轉換錯誤: {ts}")
    return ts


def read_sheet():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get("values", [])

    if not values:
        print("⚠️ 沒有資料。")
        return

    headers = values[0]
    for row in values[1:]:
        print(row)
        data = dict(zip(headers, row))
        ts = data.get("時間戳記", "")
        data["標準化時間"] = normalize_timestamp(ts)
        print(data)

if __name__ == "__main__":
    read_sheet()