from ibapi.client import *
from ibapi.contract import ContractDetails
from ibapi.wrapper import *
import time

class TestApp(EClient, EWrapper) :
    def __init__(self):
        EClient.__init__(self, self)

    def contractDetails(self, reqId, contractDetails):
        print(f'Contract Details: {contractDetails}')

    def contractDetailsEnd(self, reqId):
        print(f'End of Contract Details')
        self.disconnect()

def main():
    app = TestApp()

    app.connect("127.0.0.1", 7497, 114)
    
    mycontract = Contract()
    mycontract.symbol = 'AAPL'
    mycontract.secType = 'STK'
    mycontract.exchange = 'SMART'
    mycontract.currency = 'USD'
    mycontract.primaryExchange = 'ISLAND'

    #for options
    #mycontract.right = 'C'
    #mycontract.lastTradeDateOrContractMonth = '202209'
    #mycontract.strike = 125

    time.sleep(3)

    app.reqContractDetails(1, mycontract)

    app.run()

if __name__ == "__main__" :
    main()


