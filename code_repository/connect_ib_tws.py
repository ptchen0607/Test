#########import modules ######################
import pandas as pd
from ib_insync import *
##############################################

##########decalre constant variables##########
#connection info
local_ip = '127.0.0.1'
socket_port = 7497
client_id = 119

#account info
acc_num = 'DU008'

#text output
#connection success
connect_info_suceess = 'Connect to IB Trader Workstation successfully'
##############################################

##########connect to ib_tws###################
util.startLoop() # 開啟 Socket 線程
ib = IB()
ib.connect(local_ip, socket_port, clientId = client_id)
print(connect_info_suceess)
##############################################


############account summary info#############
# 先取得帳戶總覽，'acc_num 是我的 demo 帳號代碼，記得要改成你的 demo 帳號代碼，在 TWS 的右上方尋找
account_summary = ib.accountSummary(account = acc_num)
# 再透過 pandas 轉換為 DataFrame
account_summary_df = pd.DataFrame(account_summary).set_index('tag')

#取得 Cash 現金的數字
acc_cash = account_summary_df.loc['AvailableFunds']
#取得 Securities Gross Position Value 持有中資產的帳面價值
acc_sec_gross_pos_val = account_summary_df.loc['GrossPositionValue']
#取得 Net Liquidation Value 帳戶清算的總價值
acc_net_liq_val = account_summary_df.loc['NetLiquidation']

#print (f'Cash : {acc_cash}')
#print (f'Securities Gross Position Value : {acc_sec_gross_pos_val}')
#print (f'Net Liquidation Value : {acc_net_liq_val}')
##############################################

############  place order  ###################
# sceurityies type
sec_type = 'STK' #stock

# symbol
sym_tsla = 'TSLA'
sym_qqq = 'QQQ'

#currency
curry_usd = 'USD'

#order action
action_buy = 'BUY'
action_sell = 'SELL'

#order type
typ_market = 'MKT'
typ_lmt = 'LMT'
lmt_pirce = 370

#example: Buy TSLA 50 shares @ market
# 定義 contract 合約
contract_stk_tsla = Contract(
    secType='STK',      # 買進的是「股票」，就鍵入「STK」
    symbol='TSLA',      # 鍵入股票代碼
    exchange='SMART',   # SMART 指的是 TWS 的智能路由/ one of the router，
                        # 它會根據以下條件找出最佳的交易所
                        # 1.交易所成本最小化
                        # 2.執行機率最大化
    currency='USD'      # 鍵入貨幣單位
)
# 定義 order 委託單
order_buy_tsla_mkt = Order(
    action='BUY',       # 買進的話就是「BUY」，賣出/放空則是「SELL」
    totalQuantity=50,   # 這裡要鍵入的是「股」數喔！
    orderType='MKT'     # 例1下的是「市價單」，參數就是「MKT」
)

# 向 TWS 發送委託單！
#ib.placeOrder(contract, order)

#example: Buy QQQ 100 shares @ 370 lmt
# 定義 contract 合約
contract_stk_qqq = Contract(
    secType='STK',      # 買進「ETF」的話也是鍵入「STK」
    symbol='QQQ',       # 鍵入 ETF 代碼
    exchange='SMART',
    currency='USD'
)
# 定義 order 委託單
order_buy_qqq_lmt_370 = Order(
    action='BUY',
    totalQuantity=50,  # 這裡要鍵入的是「股」數喔！
    orderType='LMT',    # 例2下的是「限價單」，參數就是「LMT」
    lmtPrice=370,       # 限價單會多一個參數，設定「掛單價格」★
)
# 向 TWS 發送委託單！
#ib.placeOrder(contract_stk_qqq, order_buy_qqq_lmt_370)
##############################################



####### get orders status info#########

#step 1. check orders filled
# 透過這個函數，可以確認交易執行的情況
#ib.executions()
#備註：如果所有委託單都沒有成交，就會回傳一個空的 list

#return filled orders
def chk_filled_order():
    status = ib.executions()
    if bool(status) :
        print(status)
    else :
        print('No orders filled')


#step 2. retrived placed order info
# 透過這個函數，可以取得未執行完畢的交易委託
open_trades = ib.openTrades()
#檢視了一下 open_trades 會發現資訊量過多，各位針對自己所需去取值即可。這裡簡單做個示範，整理出一個記載重點資訊的 DataFrame

# 寫函數，從 open_trades 中的每一筆物件取值
def open_trade_info(trade_object):
    return {
        'orderId': trade_object.order.orderId,
        'action': trade_object.order.action,
        'totalQuantity': trade_object.order.totalQuantity,
        'orderType': trade_object.order.orderType,
        'lmtPrice': trade_object.order.lmtPrice,
        'secType': trade_object.contract.secType,
        'symbol': trade_object.contract.symbol
    }
# 整理成 DataFrame
open_trades_df = pd.DataFrame(list(map(lambda x: open_trade_info(x), open_trades)))

#return placed but non-executed orders
def chk_placed_order():
    if open_trades_df.empty :
        print('All orders are executed')
    else :
        print(open_trades_df)


chk_filled_order()
chk_placed_order()
##############################################

###### check portfolio positions##############

# 透過這個函數，可以輕鬆取得投資組合的資訊
portfolio_data = ib.portfolio()
#跟例4 非常相似，我們針對自己需求，將 portfolio_data 的資訊整理成 DataFrame
# 寫函數，從 portfolio_data 中的每一筆物件取值
def portfolio_info(asset_object):
    return {
        'symbol': asset_object.contract.symbol,
        'primaryExchange': asset_object.contract.primaryExchange,
        'currency': asset_object.contract.currency,
        'position': asset_object.position,
        'marketPrice': asset_object.marketPrice,
        'marketValue': asset_object.marketValue,
        'averageCost': asset_object.averageCost,
        'unrealizedPNL': asset_object.unrealizedPNL,
        'realizedPNL': asset_object.realizedPNL
    }
# 整理成 DataFrame
portfolio_data_df = pd.DataFrame(list(map(lambda x: portfolio_info(x), portfolio_data)))

def chk_portf_pos():
    print (portfolio_data_df)

chk_portf_pos()
##############################################