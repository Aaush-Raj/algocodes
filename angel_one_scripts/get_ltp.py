from smartapi import SmartConnect, SmartWebSocket 
# import document_detail_Lax
import time
from datetime import datetime
import datetime
import random

# api_key = document_detail_Lax.api_key
# secret_key = document_detail_Lax.secret_key
# user_id = document_detail_Lax.user_id
# password = document_detail_Lax.password

api_key = 'GHs4KzGv'
user_id = 'A718575'
password = '@ankitraj1'


obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password)["data"]["refreshToken"])
jwtToken = token['data']["jwtToken"]
refreshToken = token['data']['refreshToken']
feedToken = token['data']['feedToken']

exchange = "NFO"
script_list = {"TATAMOTORS-EQ":"3456"}

def GettingLtpData():
	tradingsymbol = random.choice(list(script_list))
	symboltoken = script_list[tradingsymbol]
	LTP = obj.ltpData(exchange, tradingsymbol, symboltoken)
	# high = LTP["data"]["high"] 
	# low = LTP["data"]["low"]
	# ltp = LTP["data"]["ltp"]

	# print(f"Scirpt:{tradingsymbol}, High:{high}, Low:{low}, LTP:{ltp}")
	print(f"Scirpt:{tradingsymbol},LTP:{ltp}")
	GettingLtpData()

orderplacetime = int(9) * 60 + int(30)
timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Waiting for 9.30 AM , CURRENT TIME:{}".format(datetime.datetime.now()))

while timenow < orderplacetime:
	time.sleep(0.2)
	timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Ready for Trading, CURRENT TIME:{}".format(datetime.datetime.now()))

try:
	GettingLtpData()
except Exception as e:
	raise e

























































def place_ce_order():
    global ce_orderId,ce_strike_symbol
    try:
        ce_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'CE',expiry_day).iloc[0]
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
            "quantity": quantitp,
            "triggerprice":0
            }
        print(orderparams)
        ce_orderId =obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
        
        
        print("ORDER STATUS IS",order_status)
    except Exception as e:
        print(f"ERROR---->>>>{e}")

    	
def call_slm_order_placement():
	print("call_slm_order_placement")
    
	global  ce_sl_orderId
    
	ce_order_status = get_order_status(ce_orderId)
	ce_average_price = get_avg_price(ce_orderId)
	print("Sell Call order status is : ",call_order_status," with avg price ",call_sell_avg_price)
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
		print("Call SLM order placed with status:",call_slm_order_status)



def place_pe_order():
    global pe_orderId,pe_strike_symbol
    try:
		pe_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'PE',expiry_day).iloc[0]

        orderparams = {
            "variety": 'NORMAL',
            "tradingsymbol": pe_strike_symbol['symbol'],
            "symboltoken": pe_strike_symbol['token'],
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
        pe_orderId =obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
        
    except Exception as e:
        print(f"ERROR---->>>>{e}")

    	
def put_slm_order_placement():
	print("call_slm_order_placement")
    
	global  pe_sl_orderId
    
	pe_order_status = get_order_status(pe_orderId)
	pe_average_price = get_avg_price(pe_orderId)
	print("Sell Call order status is : ",call_order_status," with avg price ",call_sell_avg_price)
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
		print("Call SLM order placed with status:",call_slm_order_status)



def order_modify_call(number):
    ce_slm_status = get_order_status(ce_orderId)
    pe_slm_status = get_order_status(pe_orderId)
    
    if ce_order_status == 'trigger pending':
        ce_modify_orderparams = {"variety": 'NORMAL',"orderid": ce_orderId,"ordertype": 'MARKET',"producttype": 'INTRADAY',"transactiontype": "SELL","duration": 'DAY',"price": 0,"quantity": quantity,"tradingsymbol": ce_strike_symbol['symbol'],"symboltoken": ce_strike_symbol['token'],"exchange": 'NFO'}
        modifyOrder(ce_modify_orderparams)
	else:
		print("Order is either cancelled or completed")
    
    if pe_order_status == 'trigger pending':
        pe_modify_orderparams = {"variety": 'NORMAL',"orderid": pe_orderId,"ordertype": 'MARKET',"producttype": 'INTRADAY',"transactiontype": "SELL","duration": 'DAY',"price": 0,"quantity": quantity,"tradingsymbol": pe_strike_symbol['symbol'],"symboltoken": pe_strike_symbol['token'],"exchange": 'NFO'}
        modifyOrder(pe_modify_orderparams)

	else:
		print("Order is either cancelled or completed")
    

