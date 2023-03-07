from alice_blue import *
import requests, json
import dateutil.parser
import sys
import math
import time
import pandas as pd
import datetime as dt
# from datetime import date,timedelta
from datetime import datetime, timedelta



def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)


access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
                  access_token=access_token)


#------------------------------------------LOGIC FOR GETTING HIGH AND LOW DATA--------------------------------------------------





def get_historical(instrument, from_datetime, to_datetime, interval, indices=False):
    params = {"token": instrument.token,
              "exchange": instrument.exchange if not indices else "NSE_INDICES",
              "starttime": str(int(from_datetime.timestamp())),
              "endtime": str(int(to_datetime.timestamp())),
              "candletype": 3 if interval.upper() == "DAY" else (2 if interval.upper().split("_")[1] == "HR" else 1),
              "data_duration": None if interval.upper() == "DAY" else interval.split("_")[0]}
    lst = requests.get(
        f" https://ant.aliceblueonline.com/api/v1/charts/tdv?", params=params).json()["data"]["candles"]
    records = []
    for i in lst:
        record = {"date": dateutil.parser.parse(i[0]), "open": i[1], "high": i[2], "low": i[3], "close": i[4], "volume": i[5]}
        records.append(record)
    return records


instrument = alice.get_instrument_by_symbol("NSE", "Nifty Bank")
# from_datetime = datetime.now() - timedelta(hours=10)
from_datetime = datetime.now() - timedelta(hours=4)
to_datetime = datetime.now()
interval = "1_MIN"   # ["DAY", "1_HR", "3_HR", "1_MIN", "5_MIN", "15_MIN", "60_MIN"]
indices = True
pd.set_option("max_columns", None) 
pd.set_option("max_rows", None)
df = pd.DataFrame(get_historical(instrument, from_datetime, to_datetime, interval, indices))
high_list = []
df_high = df.iloc[:,2]
df_low = df.iloc[:,3]
for h in df_high:
    high_list.append(h)
# print("THIS IS THE LIST OF ALL THE HIGHEST VALUE OF TODAY's TIMEFRAME",high_list)
highest_number = high_list[0]
for high in high_list:
    if high > highest_number:
        highest_number = high
        
print ("The highest of Banknifty since 9:15 AM is -->",strGreen(highest_number))


    
    
low_list = []
for l in df_low:
    low_list.append(l)
# print("THIS IS THE LIST OF ALL THE LowestVALUE OF TODAY's TIMEFRAME",low_list)
lowest_number = low_list[0]
for low in low_list:
    if low < lowest_number:
        lowest_number = low
        
print("The Lowest of Banknifty since 9:15 AM is -->",strGreen(lowest_number))








#------------------------------------------------------------Placing Orders and other Logics----------------------------------



symbol = 'Nifty Bank'
bnf_script = alice.get_instrument_by_symbol('NSE', symbol)

time.sleep(2)
socket_opened = False
lot_size = 1
quantity = lot_size*(25) 
print("Lot size =" ,strGreen(lot_size) , "and Quantity = " ,strGreen(quantity))



def event_handler_quote_update(message):
    global ltp_bnf
    ltp_bnf = message['ltp']
#     print(ltp_bnf)
    

def open_callback():
    global socket_opened
    socket_opened = True


alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)

while(socket_opened == False):
    pass

alice.subscribe(bnf_script, LiveFeedType.COMPACT)
time.sleep(5)

def open_socket_now():
    global socket_opened
    socket_opened = False
    alice.start_websocket(subscribe_callback=event_handler_quote_update,
                          socket_open_callback=open_callback, run_in_background=True)
    time.sleep(2)

    while (socket_opened == False):
        pass


if socket_opened == False:
    open_socket_now()
    
def latest_expiry():
    call = None
    exp_d = 0
    date_today = date.today()
    while call ==None:
        call = alice.get_instrument_for_fno(symbol="BANKNIFTY", expiry_date=date_today, is_fut=True, strike=ltp_bnf, is_CE=False)
        if call ==None:
            date_today = date_today + timedelta(days=1)
        elif call != None:
            exp_d = date_today
            return exp_d
            break

expiry_date =latest_expiry()
print("Latest expiry is on", strGreen(expiry_date))
bn_fut = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=expiry_date, is_fut=True, strike=ltp_bnf, is_CE = False)

def order_status(oid):    
    order_details =alice.get_order_history(oid)
    order_status = order_details['data'][0]['order_status']
    return order_status
    

def ap_generator(oid):
    order_details =alice.get_order_history(int(oid))
    avg_price = order_details['data'][0]['average_price']
    return avg_price



def buy_bn_fut():
    global sl_buy_fut_oid
    buy_call_fut = alice.place_order(transaction_type = TransactionType.Buy,
                             instrument = bn_fut,
                             quantity = quantity,
                             order_type = OrderType.Market,
                             product_type = ProductType.Intraday)
    
    buy_ce_oid = buy_call_fut['data']['oms_order_id']
    buy_ce_avg_price =ap_generator(buy_ce_oid)
    
    limit_price_buy_sl = float(0.05* round((buy_ce_avg_price - (buy_ce_avg_price*0.25))/0.05))
    tg_price_buy = float(0.05* round((limit_price_buy_sl + 10)/0.05)) 
    

    if order_status(buy_ce_oid) == "rejected":
        print(strRed("Order isrejected so Stoploss orders won't be complete, Please try again."))
        sys.exit(0) 
    else:
        sl_buy_fut = alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = bn_fut,
                                   quantity = quantity,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   price = limit_price_buy_sl,
                                   trigger_price =tg_price_buy,
                                   stop_loss = None,
                                   is_amo = False)
        
        sl_buy_fut_oid =sl_buy_fut['data']['oms_order_id']
        
    print(strGreen("All Orders complete Successfully! Now Just wait till 3:10PM. "))


    
    
def sell_bn_fut():
    global sl_sell_fut_oid
    sell_fut = alice.place_order(transaction_type = TransactionType.Sell,
                             instrument = bn_fut,
                             quantity = quantity,
                             order_type = OrderType.Market,
                             product_type = ProductType.Intraday)
    
    sell_fut_oid = sell_fut['data']['oms_order_id']
    sell_fut_avg_price =ap_generator(sell_fut_oid)
    
    limit_price_sell_sl = float(0.05* round((sell_fut_avg_price - (sell_fut_avg_price*0.25))/0.05))
    tg_price_sell = float(0.05* round((limit_price_sell_sl + 10)/0.05)) 
    
    
    if order_status(buy_pe_oid) == "rejected":
        print(strRed("Order isrejected so Stoploss orders won't be complete, Please try again."))
        sys.exit(0) 
    else:
        sl_sell_fut =alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = bn_fut,
                                   quantity = quantity,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   price = limit_price_sell_sl,
                                   trigger_price =tg_price_sell,
                                   stop_loss = None,
                                   is_amo = False)
        sl_sell_fut_oid =sl_sell_fut['data']['oms_order_id']
        
    print(strGreen("All Orders complete Successfully! Now Just wait till 3:10PM. "))
    

while datetime.now().time() < dt.time(14,30,30):
    time.sleep(5)
    print("WHILE LOOP FOR COMPAIRING LTP IS RUNNING!")
    if ltp_bfn > highest_number:
        print("LTP of Banknifty Broke its High since 10:00 AM , so we are now buying BN Future's Call")
        buy_bn_fut()
        break

    if ltp_bnf < lowest_number:
        print("LTP of Banknifty Broke its low since 10:00 AM , so we are now buying BN Future's PUT")
        sell_bn_fut()
        break        

        
def exit_orders():
    if order_status(sl_buy_fut_oid) == "trigger pending":
        print("SL of Call order is Still pending , so we it will get cancelled at specefied time.")
        alice.modify_order(transaction_type = TransactionType.Sell,
                           instrument = bn_fut,
                           quantity = quantity,
                           order_type = OrderType.Market,
                           product_type = ProductType.Intraday,
                           order_id=str(sl_buy_fut_oid))
    
    else:
        print("SL of Call order has been executed.So we will not place any exit orders now")
        
    if order_status(sl_sell_fut_oid) == "trigger pending":
        print("SL of PUT order is Still pending , so we it will get cancelled at specefied time.")
        alice.modify_order(transaction_type = TransactionType.Buy,
                           instrument = bn_fut,
                           quantity = quantity,
                           order_type = OrderType.Market,
                           product_type = ProductType.Intraday,
                           order_id=str(sl_sell_fut_oid))
    else:
        print("SL of PUT order has been executed.So we will not place any exit orders now")
    