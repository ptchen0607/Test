from ib_insync import *
import yfinance as yf
import pandas as pd

# Connect API
ib= IB()
ib.connect('', '', '')

# Define the asset
contract = ('AAPL', 'SMART', 'USD')

# Fetch data from yahoo finance
data= yf.download('AAPL', start = '2020-01-01', end = '2022-12-31')

# Cal moving avg
data['MA50'] = data['Close'].rolling(window=50, min_period= 1).mean()
data['MA200'] = data['Close'].rolling(window=200, min_period= 1).mean()

# Create signal
data['buy_signal'] = (data ['MA50']> data['MA200'])
data['sell_signal'] = (data ['MA50']< data['MA200'])

# Check if the market is open
exchange_hrs = ib.reqMarketDataType(contract)
if exchange_hrs:

    # Check for buy signal
    if data ['buy_signal'].iloc[-1]:
        order = MarketOrder('Buy', 100)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1) #wait a sec for the trade to execute

    # Check for the sell signal
    elif data ['sell_signal'].iloc[-1]:
        order = MarketOrder('Sell', 100)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)#wait a sec for the trade to execute

ib.disconnect()