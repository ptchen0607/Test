import datetime
import time
import pytz

#import get market data module
import get_mkt_data_module as mkt_data

import place_order_module as place_order

#美股開盤時間 @US/Eastern time
opn_hr = 1
opn_min = 0
cls_hr = 16
cls_min = 0

#convert to US/Eastern time
timezone_US = pytz.timezone('US/Eastern')
#initialize current time(now)
current_time = datetime.datetime.now(timezone_US)
now = datetime.time(current_time.hour, current_time.minute, current_time.second)


#if market hasn't start, discoonnect with ib tws
if datetime.time(opn_hr, opn_min) <= now <= datetime.time(cls_hr, cls_min):
	print(f'exec start time: {now}')
else:
	print(f'Current time: {now}, Market has NOT open yet.')


#watch list order details
sym = 'AAPL'
curry = 'USD'
act_b = 'BUY'
act_s = 'SELL'
qty_b = 10
qty_s = 5

#initialize watch list market data param details
timeframe = 1 #i-min candel bar

app = place_order.IBapi()
def run_loop():
	app.run()

#Functioon to Place order
#contract object input 1. sympol 2. currency.
#order object input 1. action 2. quantity 3.price(for limit order, optional)
#fn(input1 = sympol, input2 = currency, input3 = action, input4 = qty, input5. = price)
def fn_place_order(sym, curry, act, qty, price=None):
	if price is None:
		app.placeOrder(app.nextorderId, place_order.Stock_contract(sym, curry), place_order.Order_det_mkt(act, qty))
		app.nextorderId += 1
	else:
		app.placeOrder(app.nextorderId, place_order.Stock_contract(sym, curry), place_order.Order_det_lmt(act, qty, price))
		app.nextorderId += 1

while datetime.time(opn_hr, opn_min) <= now <= datetime.time(cls_hr, cls_min):
	#conver to US/Eastern time and updating the time(now)
	timezone_US = pytz.timezone('US/Eastern')
	current_time = datetime.datetime.now(timezone_US)
	now = datetime.time(current_time.hour, current_time.minute, current_time.second)

	from_time = current_time - datetime.timedelta(days=1) 

	#establish connection
	#connect to IB TWS
	app.connect('127.0.0.1', 7497, 1234)
	#initial nextorderId
	app.nextorderId = None
	#Start the socket in a thread
	api_thread = place_order.threading.Thread(target=run_loop, daemon=True)
	api_thread.start()
	#Check if the API is connected via orderid
	while True:
		if isinstance(app.nextorderId, int):
			print('connected')
			break
		else:
			print('waiting for connection')
			time.sleep(1)

	if datetime.time(opn_hr, opn_min) <= now <= datetime.time(cls_hr, cls_min):
		#start trading strategy
		print(f'exec updated time: {now}')

		#trigger strategy if close price > given sma buy, close price < givien sma sell, by testing set given contract info fixed.
		#And reconnect after every statement
		if mkt_data.fn_get_con_price_attr(sym,'c') > mkt_data.fn_get_con_sma(sym,timeframe,from_time,current_time,10)[mkt_data.sma_name].values[-1:]:
			fn_place_order(sym, curry, act_b, qty_b)
			current_price = mkt_data.fn_get_con_price_attr(sym,'c')
			SMA = mkt_data.fn_get_con_sma(sym,timeframe,from_time,current_time,10)[mkt_data.sma_name].values[-1:]
			app.disconnect()
			print(f'current:{current_price}, SMA{SMA}, time:{now}')
			time.sleep(10)
			print('reconnect to re-run strategy')
		elif mkt_data.fn_get_con_price_attr(sym,'c') < mkt_data.fn_get_con_sma(sym,timeframe,from_time,current_time,15)[mkt_data.sma_name].values[-1:]:
			fn_place_order(sym, curry, act_s, qty_s)
			current_price = mkt_data.fn_get_con_price_attr(sym,'c')
			SMA = mkt_data.fn_get_con_sma(sym,timeframe,from_time,current_time,10)[mkt_data.sma_name].values[-1:]
			app.disconnect()
			print(f'current:{current_price}, SMA{SMA}, time:{now}')
			time.sleep(10)
			print('reconnect to re-run strategy')
		#if no order make disconnect/reconnect
		else:
			app.disconnect()
			time.sleep(10)
	else:
		print(f'exec final time: {now}, Marketet closed')
		break
	time.sleep(3)

#call account summary after market closed.
#ib....
time.sleep(1)
app.disconnect()