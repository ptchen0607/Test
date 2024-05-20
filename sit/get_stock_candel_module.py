# stock_data_module.py
from datetime import datetime
import polygon
import pandas as pd
import pytz

class StockDataModule:
    def __init__(self, api_key):
        self.api_key = api_key
        self.stocks_client = polygon.StocksClient(api_key)

    #適用大時間範圍，並不限制筆數
    def get_historical_data(self, symbol, from_date, to_date, multiplier=30, timespan="minute", timezone='America/New_York'):

        #處理錯誤訊息，返回json資料中如不包含""results"則raise exception
        try:
            data = self.stocks_client.get_aggregate_bars(symbol=symbol, from_date=from_date, to_date=to_date,
                                                     multiplier=multiplier, timespan=timespan)
            results = data["results"]
        except KeyError:
            raise ValueError("請選擇有效的交易日")
        

        data = self.stocks_client.get_aggregate_bars(symbol=symbol, from_date=from_date, to_date=to_date,
                                                     multiplier=multiplier, timespan=timespan)
        results = data["results"]
        df = pd.DataFrame(results)

        new_columns = ["trade_date_time", "open", "close", "high", "low", "volume", "volume_weighted", "transactions"]
        new_column_names = {
            "t": "trade_date_time",
            "o": "open",
            "c": "close",
            "h": "high",
            "l": "low",
            "v": "volume",
            "vw": "volume_weighted",
            "n": "transactions"
        }

        df = df.rename(columns=new_column_names)[new_columns]
        df["trade_date_time"] = pd.to_datetime(df["trade_date_time"], unit="ms")
        df["trade_date_time"] = df["trade_date_time"].dt.tz_localize(pytz.UTC)
        df["trade_date_time"] = df["trade_date_time"].dt.tz_convert(timezone)

        # 添加 is_market_open 欄位
        df["is_market_open"] = "N"
        # 檢查開盤時間是否在市場開放時間內，並將 is_market_open 設置為 "Y"
        market_open_time = pd.Timestamp("09:30").tz_localize("America/New_York")
        market_close_time = pd.Timestamp("16:00").tz_localize("America/New_York")
        df.loc[(df["trade_date_time"].dt.time >= market_open_time.time()) & (df["trade_date_time"].dt.time <= market_close_time.time()), "is_market_open"] = "Y"

        #新增欄位 symble, updated_date
        df["symble"] = symbol
        df["updated_date"] = datetime.now()


        return df
    
    #適用最新一根蠟燭資訊，並限制返回一筆
    def get_historical_data_latest(self, symbol, from_date, to_date, multiplier=30, timespan="minute", timezone='America/New_York'):

        #處理錯誤訊息，返回json資料中如不包含""results"則raise exception
        try:
            data = self.stocks_client.get_aggregate_bars(symbol=symbol, from_date=from_date, to_date=to_date,
                                                     multiplier=multiplier, timespan=timespan)
            results = data["results"]
        except KeyError:
            raise ValueError("請選擇有效的交易日")
        
        data = self.stocks_client.get_aggregate_bars(symbol=symbol, from_date=from_date, to_date=to_date,
                                                     multiplier=multiplier, timespan=timespan)
        results = data["results"]
        df = pd.DataFrame(results)

        new_columns = ["trade_date_time", "open", "close", "high", "low", "volume", "volume_weighted", "transactions"]
        new_column_names = {
            "t": "trade_date_time",
            "o": "open",
            "c": "close",
            "h": "high",
            "l": "low",
            "v": "volume",
            "vw": "volume_weighted",
            "n": "transactions"
        }

        df = df.rename(columns=new_column_names)[new_columns]
        df["trade_date_time"] = pd.to_datetime(df["trade_date_time"], unit="ms")
        df["trade_date_time"] = df["trade_date_time"].dt.tz_localize(pytz.UTC)
        df["trade_date_time"] = df["trade_date_time"].dt.tz_convert(timezone)

        # 添加 is_market_open 欄位
        df["is_market_open"] = "N"
        # 檢查開盤時間是否在市場開放時間內，並將 is_market_open 設置為 "Y"
        market_open_time = pd.Timestamp("09:30").tz_localize("America/New_York")
        market_close_time = pd.Timestamp("16:00").tz_localize("America/New_York")
        df.loc[(df["trade_date_time"].dt.time >= market_open_time.time()) & (df["trade_date_time"].dt.time <= market_close_time.time()), "is_market_open"] = "Y"

        #新增欄位 symble, updated_date
        df["symble"] = symbol
        df["updated_date"] = datetime.now()


        return df.iloc[-1]
