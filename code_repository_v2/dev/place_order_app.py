import place_order_module as place_order
import time



app = place_order.IBapi()
app.connect('127.0.0.1', 7497, 101)

app.nextorderId = None


def run_loop():
	app.run()

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

#Function to Cancel order
#1. input the oder id expect to cancel
#fn(input1 = oderId)
def fn_cancel_order(orderid):
	print('cancelling order')
	app.cancelOrder(orderid, '')
	

#place order by function, examples:
fn_place_order('AAPL','USD','BUY',100,180)
#fn_place_order('NVDA','USD','BUY',50)

#cancel order by function, examples:
#fn_cancel_order(3)

time.sleep(1)
app.disconnect()

