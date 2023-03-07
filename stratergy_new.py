from alice_blue import *
import math
import time
import datetime
from datetime import date,timedelta


def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)



access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
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

bnf_nearest_strike = nearest_strike_bnf(ltp_bnf)
alice.unsubscribe(bnf_script, LiveFeedType.COMPACT)


def latest_expiry():
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

expiry_date =latest_expiry()

bn_ce_trade = alice.get_instrument_for_fno(symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=bnf_nearest_strike, is_CE=True)

bn_pe_trade = alice.get_instrument_for_fno(symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=bnf_nearest_strike, is_CE=False)


print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ORDER EXECUTION STARTS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
print("LATEST STRIKE PRICE IS",bnf_nearest_strike)
print("EXPIRY DATE IS",expiry_date)


def sell_atm_options():
    global bn_ce_sell_order_price,bn_pe_sell_order_price,sl_bn_ce_sell,tgp_bn_ce_sell,sl_bn_pe_sell,tgp_bn_pe_sell
    sell_call_order = alice.place_order(TransactionType.Sell,
                                        instrument = bn_ce_trade,
                                        quantity = 25,
                                        order_type = OrderType.Market,
                                        product_type = ProductType.Intraday)

    sell_put_order = alice.place_order(TransactionType.Sell,
                                        instrument = bn_pe_trade,
                                        quantity = 25,
                                        order_type = OrderType.Market,
                                        product_type = ProductType.Intraday)
    
    bn_ce_sell_order_id = sell_call_order['data']['oms_order_id']
    bn_ce_sell_order_details =alice.get_order_history(int(bn_ce_sell_order_id))
    bn_ce_sell_order_price = bn_ce_sell_order_details['data'][0]['average_price']

    bn_pe_sell_order_id = sell_put_order['data']['oms_order_id']
    bn_pe_sell_order_details =alice.get_order_history(int(bn_pe_sell_order_id))
    bn_pe_sell_order_price = bn_pe_sell_order_details['data'][0]['average_price']
    
    print("%%%%--- ORDER PLACEMENT----%%%%",sell_call_order,sell_put_order)
    

    #stoploss amount generation code
    sl_bn_ce_sell = float(int(bn_ce_sell_order_price + (bn_ce_sell_order_price*0.25)))
    tgp_bn_ce_sell = float(int(sl_bn_ce_sell + 10 ))

    sl_bn_pe_sell = float(int(bn_pe_sell_order_price + (bn_pe_sell_order_price*0.25)))
    tgp_bn_pe_sell = float(int(sl_bn_pe_sell + 10 ))

    print("CALL ORDER SL DETAILS--",sl_bn_ce_sell,tgp_bn_ce_sell)
    print("PUT ORDER SL DETAILS--",sl_bn_pe_sell,tgp_bn_pe_sell)

def stoploss_order():
    global sl_ce_oid,sl_pe_oid
    sl_ce_order = alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = bn_ce_trade,
                                   quantity = 25,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   
                                   trigger_price =tgp_bn_ce_sell,
                                   stop_loss = sl_bn_ce_sell,
                                   is_amo = False)

    sl_pe_order = alice.place_order(transaction_type = TransactionType.Buy,
                     instrument =  bn_pe_trade,
                                   quantity = 25,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   trigger_price =tgp_bn_pe_sell,
                                   stop_loss = sl_bn_pe_sell,
                                   is_amo = False)

    print("%%%%SL ORDER PLACEMENT%%%%",sl_ce_order,sl_pe_order)

    sl_ce_oid = sl_ce_order['data']['oms_order_id']
    sl_pe_oid = sl_pe_order['data']['oms_order_id']
    



order_placed = False
while datetime.datetime.now().time() < datetime.time(11,46):
    print("wait for the time to be 11:46 ; Right now the time is only -->)",datetime.datetime.now().time())
    time.sleep(5)
try:
    sell_atm_options()
    stoploss_order()
    print("Orders Placed Successfully!")
    
   
except Exception as e:
    print(f"ERROR---->>>>{e}")

    
def exit_orders():
    #WHEN TIME IS 3:10 ---ORDER CLOSING LOGIC
    alice.cancel_order(sl_ce_oid)
    alice.cancel_order(sl_pe_oid)

    #PlACE OPPOSITE ORDERS FOR CLOSING CURRENT POSITIONS-->
    
    #bn sell call order opposite 
    exit_ce_sell = alice.place_order(TransactionType.Buy,
                                        instrument = bn_ce_trade,
                                        quantity = 25,
                                        order_type = OrderType.Market,
                                        product_type = ProductType.Intraday)
    #bn sell Put order opposite 
    exit_pe_sell = alice.place_order(TransactionType.Buy,
                                        instrument = bn_pe_trade,
                                        quantity = 25,
                                        order_type = OrderType.Market,
                                        product_type = ProductType.Intraday)
    
    
while datetime.datetime.now().time() < datetime.time(15,10):
    print("wait for the time to be 15:10 ; Right now the time is only -->)",datetime.datetime.now().time())
    time.sleep(5)
try:
    exit_orders()
    print("DONE FOR THE DAY, HOPE YOU MADE GOOD PROFITS")
    
except Exception as e:
    print(f"ERROR---->>>>{e}")
