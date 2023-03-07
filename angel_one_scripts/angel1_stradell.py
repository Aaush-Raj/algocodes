import warnings
warnings.filterwarnings('ignore')
import math
from smartapi import SmartConnect
from nsepython import expiry_list
import time
import requests
import pandas as pd
# import datetime as dt
import datetime
from datetime import date,timedelta
import time
from smartapi import SmartConnect

apikey = 'GHs4KzGv'
username = 'A718575'
pwd = '@ankitraj1'
   

obj=SmartConnect(api_key=apikey)
data = obj.generateSession(username,pwd)
refreshToken= data['data']['refreshToken']
feedToken=obj.getfeedToken()



url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
d = requests.get(url).json()
token_df = pd.DataFrame.from_dict(d)
token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
token_df = token_df.astype({'strike': float})
#token_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']==date(2021,6,10)) ]


def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)

def getTokenInfo (symbol, exch_seg ='NSE',instrumenttype='OPTIDX',strike_price = '',pe_ce = 'CE',expiry_day = None):
    df = token_df
    strike_price = strike_price*100
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE') ]
        return eq_df[eq_df['name'] == symbol]
    elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return df[(df['exch_seg'] == 'NFO') & (df['expiry']==expiry_day) &  (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])



expiry_day = date(2022,9,1)

symbol = 'BANKNIFTY'

spot_token = getTokenInfo(symbol).iloc[0]['token']
ltpInfo = obj.ltpData('NSE',symbol,spot_token)
ltp_bnf = ltpInfo['data']['ltp']
print("BANKNIFTY LATEST PRICE IS",ltp_bnf)
ATMStrike = nearest_strike_bnf(ltp_bnf)
pe_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'PE',expiry_day).iloc[0]
ce_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'CE',expiry_day).iloc[0]


def main():
	global expiry_date

	curr_ltp=int(float(ltp_bnf))
	print(curr_ltp)

	ce,pe = round(curr_ltp/100)*100,round(curr_ltp/100)*100
	print('ATM CE ',ce,' ATM PE ',pe)
	# get_date_curr_expriry()
	expiry_date = pd.to_datetime(expiry_list('BANKNIFTY')[0])
	print("date--->",expiry_date)

	place_ce_order()
	place_pe_order()
	time.sleep(2)
	call_slm_order_placement()
	put_slm_order_placement()
	order_placed = True

	
def get_avg_price(orderid):
    OrderBook = obj.orderBook()['data']
    for i in OrderBook:
        if i['orderid'] == orderid:
            avg_price = i['averageprice']
            return avg_price
            
def get_order_status(orderid):
    OrderBook = obj.orderBook()['data']
    for i in OrderBook:
        if i['orderid'] == orderid:
            order_status = i['orderstatus']
            status_text = i['text']
            return order_status


def order_modify(number):
    ce_slm_status = get_order_status(ce_orderId)
    pe_slm_status = get_order_status(pe_orderId)
    
    if ce_order_status == 'trigger pending':
        ce_modify_orderparams = {"variety": 'NORMAL',"orderid": ce_orderId,"ordertype": 'MARKET',"producttype": 'INTRADAY',"transactiontype": "SELL","duration": 'DAY',"price": 0,"quantity": quantity,"tradingsymbol": ce_strike_symbol['symbol'],"symboltoken": ce_strike_symbol['token'],"exchange": 'NFO'}
        modifyOrder(ce_modify_orderparams)
	# else:
	# 	print("Order is either cancelled or completed")
    
    if pe_order_status == 'trigger pending':
        pe_modify_orderparams = {"variety": 'NORMAL',"orderid": pe_orderId,"ordertype": 'MARKET',"producttype": 'INTRADAY',"transactiontype": "SELL","duration": 'DAY',"price": 0,"quantity": quantity,"tradingsymbol": pe_strike_symbol['symbol'],"symboltoken": pe_strike_symbol['token'],"exchange": 'NFO'}
        modifyOrder(pe_modify_orderparams)

	# else:
	# 	print("Order is either cancelled or completed")
    


def place_ce_order():
    global ce_orderId
    try:
        orderparams = {
            "variety": 'NORMAL',
            "tradingsymbol": ce_strike_symbol['symbol'],
            "symboltoken": ce_strike_symbol['token'],
            "transactiontype": "SELL",
            "exchange": 'NFO',
            "ordertype": 'MARKET',
            "producttype": 'INTRADAY',
            "duration": "DAY",
            "price": 0,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity,
            "triggerprice":0
            }
        print(orderparams)
        ce_orderId =obj.placeOrder(orderparams)
        
        
    except Exception as e:
        print(f"ERROR---->>>>{e}")




def place_pe_order():
	global pe_orderId

	orderparams = {"variety": 'NORMAL',"tradingsymbol": pe_strike_symbol['symbol'],"symboltoken": pe_strike_symbol['token'],"transactiontype": "SELL","exchange": 'NFO',"ordertype": 'MARKET',"producttype": 'INTRADAY',"duration": "DAY","price": 0,"squareoff": "0","stoploss": "0","quantity": quantity,"triggerprice":0}
	print(orderparams)
	pe_orderId =obj.placeOrder(orderparams)




	
	
def call_slm_order_placement():
	print("call_slm_order_placement")

	global  ce_sl_orderId

	ce_order_status = get_order_status(ce_orderId)
	ce_average_price = get_avg_price(ce_orderId)
	print("Sell Call order status is : ",ce_order_status," with avg price ",ce_average_price)
	if ce_order_status == 'complete':
		slm_call_buy_price = 0.05 * round((ce_average_price * 1.20)/0.05)
		slm_limit_call_buy_price = float(round(slm_call_buy_price + 10))
		orderparams = {
			"variety": 'STOPLOSS',
			"tradingsymbol": ce_strike_symbol['symbol'],
			"symboltoken": ce_strike_symbol['token'],
			"transactiontype": "BUY",
			"exchange": 'NFO',
			"ordertype": 'STOPLOSS_LIMIT',
			"producttype": 'INTRADAY',
			"duration": "DAY",
			"price": slm_call_buy_price,
			"squareoff": "0",
			"stoploss": "0",
			"quantity": quantity,
			"triggerprice":slm_limit_call_buy_price
			}
		ce_sl_orderId =obj.placeOrder(orderparams)

	
def put_slm_order_placement():
	print("call_slm_order_placement")
    
	global  pe_sl_orderId
    
	pe_order_status = get_order_status(pe_orderId)
	pe_average_price = get_avg_price(pe_orderId)
	print("Sell Call order status is : ",pe_order_status," with avg price ",pe_average_price)
	if pe_order_status == 'complete':
		slm_call_buy_price = 0.05 * round((pe_average_price * 1.20)/0.05)
		slm_limit_call_buy_price = float(round(slm_call_buy_price + 10))
		orderparams = {
			"variety": 'STOPLOSS',
			"tradingsymbol": pe_strike_symbol['symbol'],
			"symboltoken": pe_strike_symbol['token'],
			"transactiontype": "BUY",
			"exchange": 'NFO',
			"ordertype": 'STOPLOSS_LIMIT',
			"producttype": 'INTRADAY',
			"duration": "DAY",
			"price": slm_call_buy_price,
			"squareoff": "0",
			"stoploss": "0",
			"quantity": 25,
			"triggerprice":slm_limit_call_buy_price
			}
		pe_sl_orderId =obj.placeOrder(orderparams)

#Getting All the Necessary Variables

order_placed = False
modify_order = False
symbol = 'Nifty Bank'
no_of_lots = 2
quantity=no_of_lots*int(25)
# bnf_script = alice.get_instrument_by_symbol('NSE',symbol)
socket_opened= False


if (__name__=='__main__'):
	print('started straddle')
	main()

