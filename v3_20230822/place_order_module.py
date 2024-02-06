from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

import threading #used by main DONN'T deleate

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)

	def nextValidId(self, orderId: int):
		super().nextValidId(orderId)
		self.nextorderId = orderId
		print('The next valid order id is: ', self.nextorderId)

	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
		print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
	
	def openOrder(self, orderId, contract, order, orderState):
		print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)


#Function to create FX contract
def FX_contract(symbol):
	contract = Contract()
	contract.symbol = symbol[:3]
	contract.secType = 'CASH'
	contract.exchange = 'IDEALPRO'
	contract.currency = symbol[3:]
	return contract

#Function to create Stock contract
def Stock_contract(symbol, curry):
	contract = Contract()
	contract.symbol = symbol
	contract.secType = 'STK'
	contract.exchange = 'SMART'
	contract.currency = curry
	return contract

#Function to create order details @market price
def Order_det_mkt(action, qty):
	order = Order()
	order.action = action
	order.totalQuantity = qty
	order.orderType = 'MKT'
	return order

#Function to create order details @limit price
def Order_det_lmt(action, qty, lmt_pirc):
	order = Order()
	order.action = action
	order.totalQuantity = qty
	order.orderType = 'LMT'
	order.lmtPrice = lmt_pirc
	return order
	