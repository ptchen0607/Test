import yfinance as yf
import matplotlib.pyplot as plt
# Define the stock symbol and the time period you're interested in
data= yf.download('AAPL', start = '2020-01-01', end = '2023-12-31')

# Cal moving avg
data['MA60'] = data['Close'].rolling(window=60, min_periods= 1).mean()
data['MA200'] = data['Close'].rolling(window=200, min_periods=1 ).mean()


# Plotting closing prices
plt.figure(figsize=(10, 6))
plt.plot(data['Close'], label='close price')
plt.plot(data['MA60'], label='MA60')
plt.plot(data['MA200'], label='MA200')

plt.title('AAPL Stock Analysis')
plt.xlabel('Date')
plt.ylabel('Price')
plt.grid(False)
plt.legend()
plt.show()

