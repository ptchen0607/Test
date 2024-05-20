import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from gspread.utils import rowcol_to_a1

class GoogleSheetExporter:
    def __init__(self, creds_file_path):
        self.creds_file_path = creds_file_path
        self.credentials = Credentials.from_service_account_file(creds_file_path)
        self.scoped_credentials = self.credentials.with_scopes([
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ])
        self.gc = gspread.authorize(self.scoped_credentials)

    def export_to_google_sheet(self, dataframe, spreadsheet_name, worksheet_name):
        # 開啟 Google Sheets
        sh = self.gc.open(spreadsheet_name)
        worksheet = sh.worksheet(worksheet_name) # 選擇工作表

        # 將數據框中的數據寫入工作表
        set_with_dataframe(worksheet, dataframe)
    
    def update_google_sheet(self, dataframe, spreadsheet_name, worksheet_name, start_cell):
        # 開啟 Google Sheets
        sh = self.gc.open(spreadsheet_name)
        worksheet = sh.worksheet(worksheet_name)  # 選擇工作表

        # 將第一欄和最後一欄轉換為字串
        dataframe[dataframe.columns[0]] = dataframe[dataframe.columns[0]].astype(str)
        dataframe[dataframe.columns[-1]] = dataframe[dataframe.columns[-1]].astype(str)

        # 將 DataFrame 轉換為二維列表，並將 Timestamp 轉換為字串
        data = dataframe.values.tolist()

        # 獲取 DataFrame 的形狀（行和列數）
        num_rows, num_cols = dataframe.shape

        # 計算要更新的單元格範圍的起始和結束
        start_row, start_col = start_cell
        end_row = start_row + num_rows - 1
        end_col = start_col + num_cols - 1

        # 更新指定範圍的數據
        cell_list = worksheet.range(start_row, start_col, end_row, end_col)
        for i, cell in enumerate(cell_list):
             cell.value = data[i // num_cols][i % num_cols]
        worksheet.update_cells(cell_list)


class GoogleSheetFetcher:
    def __init__(self, creds_file_path):
        self.creds_file_path = creds_file_path
        self.credentials = Credentials.from_service_account_file(creds_file_path)
        self.scoped_credentials = self.credentials.with_scopes([
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ])
        self.gc = gspread.authorize(self.scoped_credentials)
    
    def fetching_from_google_sheet(self, spreadsheet_name, worksheet_name):
        # Access a specific worksheet in the Google Sheet
        sh = self.gc.open(spreadsheet_name)
        worksheet = sh.worksheet(worksheet_name)  

         # Read data from columns 3 to 5 (columns C to E)
        data = []
        for i in range(3, 6):
            column_data = worksheet.col_values(i)[1:]  # Exclude header
            data.append(column_data)

        # Transpose the data to have lists of rows instead of columns
        data = list(zip(*data))
        df = pd.DataFrame(data, columns=['Close', 'High', 'Low'])

        return df
    
class GoogleSheetResultWriter:
    def __init__(self, creds_file_path):
        self.creds_file_path = creds_file_path
        self.credentials = Credentials.from_service_account_file(creds_file_path)
        self.scoped_credentials = self.credentials.with_scopes([
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ])
        self.gc = gspread.authorize(self.scoped_credentials)
    
    

    def sending_signal(self, column_data, spreadsheet_name, worksheet_name):

        sh = self.gc.open(spreadsheet_name)
        worksheet = sh.worksheet(worksheet_name)  
        # Specify the column to write to (e.g., column C)
        column_index = 12  # Modify with the desired column index (1-based)
        # Find the first empty cell in the column
        cell_list = worksheet.col_values(column_index)
        empty_cell_index = len(cell_list) + 1  # Index of the first empty cell
         # Prepare data in the format expected by gspread (list of list for each row)
        values = [[value] for value in column_data]
        # Update in batches
        batch_size = 1000
        for start in range(0, len(values), batch_size):
            # Calculate end index, ensuring we don't exceed the length of the list
            end = start + batch_size

            # Range for the batch update
            range_start = rowcol_to_a1(empty_cell_index + start, column_index)
            range_end = rowcol_to_a1(min(empty_cell_index + end - 1, empty_cell_index + len(values) - 1), column_index)
            cell_range = f'{range_start}:{range_end}'

            # Update the worksheet in a batch
            worksheet.update(cell_range, values[start:end])