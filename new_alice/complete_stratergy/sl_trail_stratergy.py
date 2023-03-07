from alice_blue import *
import sys
import math
import time
import datetime
from datetime import date,timedelta


def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)



access_token = AliceBlue.login_and_get_access_token(username="",
                                                    password="",
                                                    twoFA='',
                                                    api_secret='',
                                                    app_id='')

alice = AliceBlue(username='', password="",
                  access_token=access_token)

symbol = 'Nifty Bank'
bnf_script = alice.get_instrument_by_symbol('NSE', symbol)

time.sleep(2)
socket_opened = False


def event_handler_quote_update(message):
    global ltp_bnf
    ltp_bnf = message['ltp']

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

def latest_expiry(bnf_nearest_strike):
    call = None
    exp_d = 0
    date_today = date.today()
    while call ==None:
        call = alice.get_instrument_for_fno(symbol="BANKNIFTY", expiry_date=date_today, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
        if call ==None:
            date_today = date_today + timedelta(days=1)
        elif call != None:
            exp_d = date_today
            return exp_d
            break




def order_status(oid):    
    order_details =alice.get_order_history(oid)
    order_status = order_details['data'][0]['order_status']
    return order_status
    

def ap_generator(oid):
    order_details =alice.get_order_history(int(oid))
    avg_price = order_details['data'][0]['average_price']
    return avg_price


def sell_atm_options():
    global ce_sell_avg_price, pe_sell_avg_price, bn_ce_sell_order_id, bn_pe_sell_order_id
    sell_call_order = alice.place_order(TransactionType.Sell,
                                        instrument = bn_ce_trade,
                                        quantity = quantity,
                                        order_type = OrderType.Market,
                                        product_type = ProductType.Intraday)

    sell_put_order = alice.place_order(TransactionType.Sell,
                                        instrument = bn_pe_trade,
                                        quantity = quantity,
                                        order_type = OrderType.Market,
                                        product_type = ProductType.Intraday)
    
    bn_ce_sell_order_id = sell_call_order['data']['oms_order_id']
    bn_pe_sell_order_id = sell_put_order['data']['oms_order_id']
    ce_sell_avg_price =ap_generator(bn_ce_sell_order_id) 
    pe_sell_avg_price =ap_generator(bn_pe_sell_order_id)
    
    print("%%%%--- ORDER complete----%%%%",sell_call_order,sell_put_order)

def stoploss_order():
    global sl_ce_oid,sl_pe_oid
    sl_ce_order = alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = bn_ce_trade,
                                   quantity = quantity,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   price = limit_price_ce,
                                   trigger_price =tgp_bn_ce_sell,
                                   stop_loss = None,
                                   is_amo = False)

    sl_pe_order = alice.place_order(transaction_type = TransactionType.Buy,
                     instrument =  bn_pe_trade,
                                   quantity = quantity,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   price = limit_price_pe,
                                   trigger_price =tgp_bn_pe_sell,
                                   stop_loss = None,
                                   is_amo = False)

    print("%%%% STOPLOSS ORDERS complete SUCCESSFULLY %%%%",sl_ce_order,sl_pe_order)
    print("CALL ORDER SL DETAILS--> Limit price is",strGreen(limit_price_ce),"and Trigger price is",strGreen(tgp_bn_ce_sell))
    print("PUT ORDER SL DETAILS--> Limit price is",strGreen(limit_price_pe),"and Trigger price is",strGreen(tgp_bn_pe_sell))



    sl_ce_oid = sl_ce_order['data']['oms_order_id']
    sl_pe_oid = sl_pe_order['data']['oms_order_id']
    
def exit_orders():
    if order_status(sl_ce_oid) == "trigger pending":
        print("SL of Call order is Still pending , so we it will get cancelled at specefied time.")
        alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_ce_trade, product_type=ProductType.Intraday, order_id=str(sl_ce_oid), order_type=OrderType.Market,quantity=quantity)
    
    else:
        print("SL of Call order has been executed.So we will not place any exit orders now")
        
    if order_status(sl_pe_oid) == "trigger pending":
        print("SL of PUT order is Still pending , so we it will get cancelled at specefied time.")
        alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_pe_trade, product_type=ProductType.Intraday, order_id=str(sl_pe_oid), order_type=OrderType.Market,quantity=quantity)
    else:
        print("SL of PUT order has been executed.So we will not place any exit orders now")
    

order_complete = False
while datetime.datetime.now().time() < datetime.time(12,19):
    print("wait for the time to be 9:20 ; Right now the time is only -->)",datetime.datetime.now().time())
    time.sleep(5)
try:
    lot_size = 1
    quantity = lot_size*(25) 
    bnf_nearest_strike = nearest_strike_bnf(ltp_bnf)
    expiry_date =latest_expiry(bnf_nearest_strike)

    print("Lot size =" ,strGreen(lot_size) , "and Quantity = " ,strGreen(quantity))
    print("Latest expiry is on", strGreen(expiry_date))
   
    bn_100_above_strike = bnf_nearest_strike + 100
    bn_100_below_strike = bnf_nearest_strike - 100
    print("banknifty LTP is ",strGreen(ltp_bnf))
    print("NEAREST STRIKE PRICE OF BANKNIFTY IS",strGreen(bnf_nearest_strike))
    alice.unsubscribe(bnf_script, LiveFeedType.COMPACT)

    bn_ce_trade = alice.get_instrument_for_fno(symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
    
    bn_pe_trade = alice.get_instrument_for_fno(symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=bnf_nearest_strike, is_CE=False)
    
    sell_atm_options()
    #stoploss CALL details
    tgp_bn_ce_sell = float(0.05* round((ce_sell_avg_price + (ce_sell_avg_price*0.05))/0.05))
    limit_price_ce = float(0.05* round((tgp_bn_ce_sell + 10)/0.05))

    #stoploss PUT details
    tgp_bn_pe_sell = float(0.05* round((pe_sell_avg_price + (pe_sell_avg_price*0.05))/0.05))
    limit_price_pe = float(0.05* round((tgp_bn_pe_sell + 10)/0.05))


    if order_status(bn_ce_sell_order_id) == "rejected" and order_status(bn_pe_sell_order_id) == "rejected":
        print(strRed("Orders are rejected so Stoploss orders won't be complete, Please try again."))
        sys.exit(0) 
    else:
        stoploss_order()
    print(strGreen("All Orders complete Successfully! Now Just wait till 3:10PM. "))
    
   
except Exception as e:
    print(strRed(f"ERROR---->>>>{e}"))
    
    
while datetime.datetime.now().time() < datetime.time(12,25):
    time.sleep(2)
    print("sl to cost is pending")
    if order_status(sl_ce_oid) == "complete": 
        print("SL of Call order has been executed so we will trail the sl of PUT side tp the cost")
        alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_pe_trade, quantity=quantity, product_type=ProductType.Intraday, order_id=str(sl_pe_oid), order_type = OrderType.StopLossLimit,price = float(pe_sell_avg_price + 10),trigger_price =pe_sell_avg_price)
        break

    if order_status(sl_pe_oid) == "complete": 
        print("SL of PUT order has been executed so we will trail the sl of CALL Side to the cost")
        alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_ce_trade, quantity=quantity, product_type=ProductType.Intraday, order_id=str(sl_ce_oid), order_type = OrderType.StopLossLimit,price = float(ce_sell_avg_price + 10),trigger_price =ce_sell_avg_price)
        break
    
    else:
        pass


while datetime.datetime.now().time() < datetime.time(15,10):
    time.sleep(5)
    print("WHILE LOOP FOR EXIT LOGIC IS RUNNING, WAIT FOR THE RIGHT TIME TO EXIT")
try:
    exit_orders()
    print("DONE FOR THE DAY, HOPE YOU MADE GOOD PROFIT.")
    
except Exception as e:
    print(strRed(f"ERROR---->>>>{e}"))