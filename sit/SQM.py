import pandas as pd
import numpy as np



def calculate_ema(data, window=200):
    ema = data.rolling(window=window).mean()
    return ema

def calculate_sqzmom(df, bb_length=20, kc_length=20, kc_mult=1.5, bb_mult=2.0, use_true_range=True):

    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    
    # Drop rows with missing or non-numeric values
    df.dropna(subset=['High', 'Low', 'Close'], inplace=True)
    source = df['Close']
    
    
    # Calculate Bollinger Bands
    basis = df['Close'].ewm(span=bb_length, adjust=False).mean()
    dev = kc_mult * df['Close'].rolling(window=bb_length).std()
    upper_bb = basis + dev
    lower_bb = basis - dev

    # Calculate Keltner Channels
    ma = df['Close'].ewm(span=kc_length, adjust=False).mean()
    range_val = df['High'] - df['Low'] if use_true_range else df['Close'].diff()
    range_ma = range_val.ewm(span=kc_length, adjust=False).mean()
    upper_kc = ma + range_ma * kc_mult
    lower_kc = ma - range_ma * kc_mult
    
    # Identify Squeeze
    sqz_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
    sqz_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)
    no_sqz = (~sqz_on) & (~sqz_off)
    
    avg_hl = (df['High'].rolling(window=kc_length).max() + df['Low'].rolling(window=kc_length).min()) / 2
    avg_hl_kc = (avg_hl + source.rolling(window=kc_length).mean()) / 2
    
    val = df['Close'] - avg_hl_kc
    val = val.rolling(window=kc_length).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
    
    '''
    #old ver of val
    val = source - avg_hl_kc
    val = calculate_ema(val, kc_length) #NOT SURE
    '''

    
    # Calculate EMA
    ema_length = 200
    ema_source = df['Close']
    ema_value = ema_source.ewm(span=ema_length, adjust=False).mean()

    column_data =[]
    # Create a variable to store the streak count
    sqz_count = 0

    # Define initial state
    position_open = False
    
    # Iterate over DataFrame rows and calculate the conditions for each data point
    for idx, row in df.iterrows():
        # Long condition
        con_ema = row['Close'] > ema_value.loc[idx]
        con_dark_green = val.shift(1).loc[idx] < val.shift(2).loc[idx]

        open_long = ((val.loc[idx] < 0) & (val.loc[idx] > val.shift(1).loc[idx]) & (~sqz_on.loc[idx]) & con_ema) | \
                    ((val.loc[idx] > 0) & (val.loc[idx] > val.shift(1).loc[idx]) & (~sqz_on.loc[idx]) & con_ema & (sqz_count >= 5))
        close_long = ((val.loc[idx] > 0) & (val.loc[idx] < val.shift(1).loc[idx]) & (row['Close'] < upper_kc.loc[idx])) | \
                     sqz_on.loc[idx] | ((val.loc[idx] < 0) & (val.loc[idx] < val.shift(1).loc[idx]) & sqz_on.loc[idx])
        
        # Increment sqz_count if sqz_on is True for the current row
        sqz_count = sqz_count + 1 if sqz_on.loc[idx] else 0

        # Check conditions and append the corresponding label to the result list
        if open_long and not position_open:
            position_open = True
            column_data.append('open_long')
        elif close_long and position_open:
            position_open = False
            column_data.append('close_long')
        elif open_long and position_open: 
            column_data.append('already_open')
        else:
            column_data.append('not_reaching_indicator')


    return column_data
        


   

    

# if __name__ == "__main__":
#     from API_import import fetching_data
#     # Example: Download historical data for a stock (e.g., AAPL) and calculate SQZMOM
#     symbol = 'AAPL_SIT'
#     data = fetching_data(symbol)
#     column_data = calculate_sqzmom(data)
#     print(column_data)
#     calculate_ema(data)


