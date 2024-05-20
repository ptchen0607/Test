from datetime import datetime, timedelta
import telegram_sender_module

#import referece module
from get_stock_candel_module import StockDataModule
from to_google_sheet_module import GoogleSheetExporter, GoogleSheetFetcher, GoogleSheetResultWriter
from SQM import calculate_sqzmom

# 設定 
#1. polygon API 金鑰, api_key
#2. Google Sheet的憑證文件路徑, creds_file_path
api_key = 'f9RCCY1PyYmsLca1D6ipuW2ny9TRDp1f'
creds_file_path = "/Users/chenbingting/Desktop/Trade_BOT/api_keys/google_sheet/trade-bot-416811-aecc9096ef2f.json"

# 初始化 StockDataModule 和 GoogleSheetExporter
stock_data_module = StockDataModule(api_key)
google_sheet_exporter = GoogleSheetExporter(creds_file_path)
google_sheet_fetcher = GoogleSheetFetcher(creds_file_path)
google_sheet_resulter = GoogleSheetResultWriter(creds_file_path)


# 取得今天日期
today = datetime.today()
targer_start_date = today - timedelta(days=7)

# 將日期格式化為字串形式（YYYY-MM-DD）
today_str = today.strftime('%Y-%m-%d')
targer_start_date_str = targer_start_date.strftime('%Y-%m-%d')

# 從 Polygon API 獲取歷史數據
symbol = 'AAPL'
start_date = targer_start_date_str
end_date = today

#日批，取得EOD市場資訊
historical_data = stock_data_module.get_historical_data(symbol, start_date, end_date)
print(historical_data)

#30分批，每30分鐘獲取新資訊，需升級Advance方案才能啟用real-time data
#historical_data_latest = stock_data_module.get_historical_data_latest(symbol, start_date, end_date)
#print(historical_data)

# 匯入到 Google Sheet 
spreadsheet_name = 'DB'
worksheet_name = 'AAPL_SIT'

#取得更新資料
sh = google_sheet_exporter.gc.open(spreadsheet_name)
worksheet = sh.worksheet(worksheet_name) # 選擇工作表


all_values = worksheet.get_all_values()
if not all_values:
    google_sheet_exporter.export_to_google_sheet(historical_data, spreadsheet_name, worksheet_name)
    msg = f'NEW: {symbol} data has been update to google work sheet:{spreadsheet_name}/{worksheet_name}'
    print(msg)
else:
    existing_rows = len(worksheet.get_all_values())
    existing_cols = len(worksheet.get_all_values()[0])

    next_row = existing_rows + 1
    next_col = existing_cols + 1

    start_cell = (existing_rows,1)

    google_sheet_exporter.update_google_sheet(historical_data, spreadsheet_name, worksheet_name, start_cell)
    msg = f'Updated: {symbol} data has been update to google work sheet:{spreadsheet_name}/{worksheet_name}'
    print(msg)

test_data = google_sheet_fetcher.fetching_from_google_sheet(spreadsheet_name, worksheet_name)
print(test_data)
msg = f'fetching data successfully'
print(msg)

data_to_be_calculated = calculate_sqzmom(google_sheet_fetcher.fetching_from_google_sheet(spreadsheet_name, worksheet_name))
google_sheet_resulter.sending_signal(data_to_be_calculated, spreadsheet_name, worksheet_name)

print('dddded')