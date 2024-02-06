import finnhub
import datetime 
import pytz
import pandas as pd

#datetime to time stamp 
#convert to US/Eastern time
timezone_US = pytz.timezone('US/Eastern')
#initialize current time(now)
current_time = datetime.datetime.now(timezone_US)
#current_time = datetime.datetime.now()
now = datetime.time(current_time.hour, current_time.minute, current_time.second)

#datetime to timestamp
def to_timestamp(date_time):
    return date_time.timestamp()

#time stamp to datetime
def to_datetime(time_stamp):
    date_time = datetime.datetime.fromtimestamp(time_stamp)
    return date_time.strftime("%Y-%m-%d, %H:%M:%S")


apiKey = 'cjhfvr1r01qu5vptlv30cjhfvr1r01qu5vptlv3g'

finnhub_client = finnhub.Client(api_key=apiKey)

#get current price(real-time) attributes
#input 1. symbole 2. attr_param
#attr_param, 'c': current price, 'd': day change, 'dp': day change in %, 'h': high, 'l': low, 'o': open, 'pc': 'previosu close price', 't': time
#fn(input1 = symbole, input2 = attr_param)
def fn_get_con_price_attr(sym, attr_param):
    data = finnhub_client.quote(sym)
    if attr_param == 't':
        return to_datetime(data.get('t'))
    else:
        return data.get(attr_param)

#Function to get contract candles datas and convert to df
#input 1. symbol 2. timeframe(the candles period, 5min, 1hr, 1d....) 3. start time 4.end time (time need to be in datetime format.)
#fn(imput1 = symbol, imput2 = timeframe, input3 = start time, input4 = end time)
def fn_get_con_candle(sym, timeframe, str_time, end_time):
    data = finnhub_client.stock_candles(sym, timeframe, int(to_timestamp(str_time)), int(to_timestamp(end_time)))
    df = pd.DataFrame.from_dict(data)
    df = df.drop('s', axis=1)
    df = df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low', 'o': 'open', 't': 'time', 'v': 'volume',})
    #convert timestamp to datetime @ us local time
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True).map(lambda x: x.tz_convert(timezone_US))

    return df

#function to caculate SMA within given param(1. windows period)
#input 1. symbol 2. timeframe(the candles period, 5min, 1hr, 1d....) 3. start time 4.end time (time need to be in datetime format.)
#fnfn(imput1 = symbol, imput2 = timeframe, input3 = start time, input4 = end time, )
def fn_get_con_sma(sym, timeframe, str_time, end_time, sma):
    #var 
    global sma_name
    sma_name = f'SMA{sma}'

    #get the contract candle df
    df = fn_get_con_candle(sym,timeframe,str_time,end_time)

    #resize contract candle df to wanted field for sma df
    df_sma = df['close'].to_frame()
    df_t = df['time'].to_frame()

    # calculating simple moving average
    # using .rolling(window).mean() ,
    # with window size = sma(e.g 30)
   
    df_sma[sma_name] = df_sma['close'].rolling(sma).mean()
    df_sma['time'] = df_t

    # removing all the NULL values using
    # dropna() method
    df_sma.dropna(inplace=True)
    return df_sma


#print(fn_get_con_candle(sym,timeframe,from_time,current_time))

#get real-time close price
#print(fn_get_con_price_attr(sym,'c'))


#get calculated sma df
#print(fn_get_con_sma(sym,timeframe,from_time,current_time,10))


#get last SMA{period} values
#print(float(fn_get_con_sma(sym,timeframe,from_time,current_time,10)[sma_name].values[-1:]))
