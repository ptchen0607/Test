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
creds_file_path = "/Users/edisonchen/Desktop/Trade_BOT/api_keys/google_sheet/trade-bot-416811-aecc9096ef2f.json"

#3. Telegram token
bot_token = "6898763009:AAEogUUa9on6XmKB6KZf1VEEyjLeZ6d2ZX4"
sender = telegram_sender_module.TelegramSender(bot_token)

# 要發送消息的多個聊天的 chat_id 列表
# BOT ID: tradingV001testbot
# Get chat_id: https://api.telegram.org/bot6898763009:AAEogUUa9on6XmKB6KZf1VEEyjLeZ6d2ZX4/getUpdates

#4. Telegram chad ID List:
'''
Telegram chat ID List:
1. Chen Wu: 6276079039
2. Edison Chen: 1390066910
3. Jeff Wang: 1206364869
4. Ying Yu: 
'''
edison_chen_id = '1390066910'
chen_wu_id = '6276079039'
jeff_wang_id = '1206364869'

#chat_ids = [chen_wu_id,edison_chen_id,jeff_wang_id]
# chat_ids_dev = [edison_chen_id, chen_wu_id, jeff_wang_id]
chat_ids_dev = [edison_chen_id]

# 初始化 StockDataModule 和 GoogleSheetExporter, GoogleSheetFetcher, GoogleSheetResultWriter
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

#send start batch workflow information via Telegram, msg1
msg1 = f'開始取得{symbol}, {start_date} ~ {end_date} 市場資訊 @ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
sender.send_message(chat_ids_dev, msg1)

#日批，取得EOD市場資訊
historical_data = stock_data_module.get_historical_data(symbol, start_date, end_date)
#print(historical_data)

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

    #send get marketdata info. via Telegram, msg2_1
    msg2_1 = f'NEW: {symbol} data has been update to google work sheet: {spreadsheet_name}/{worksheet_name} @ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    sender.send_message(chat_ids_dev, msg2_1)
else:
    existing_rows = len(worksheet.get_all_values())
    existing_cols = len(worksheet.get_all_values()[0])

    next_row = existing_rows + 1
    next_col = existing_cols + 1

    start_cell = (existing_rows,1)

    google_sheet_exporter.update_google_sheet(historical_data, spreadsheet_name, worksheet_name, start_cell)

    #send get marketdata info. via Telegram, msg2_2
    msg2_2 = f'Updated: {symbol} data has been update to google work sheet: {spreadsheet_name}/{worksheet_name} @ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    sender.send_message(chat_ids_dev, msg2_2)



#fethcing market data through google sheet which just been export and calculate throgh strategy and sending Open or close positio result 
data_to_be_calculated = calculate_sqzmom(google_sheet_fetcher.fetching_from_google_sheet(spreadsheet_name, worksheet_name))
google_sheet_resulter.sending_signal(data_to_be_calculated, spreadsheet_name, worksheet_name)

#send if Open or close positio result updated to google sheet via Telegram, msg3
strategy_name = 'SQM'
msg3 = f'{symbol} data has been calulated by Strategy: {strategy_name}, result has been updated to: {spreadsheet_name}/{worksheet_name} @ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
sender.send_message(chat_ids_dev, msg3)