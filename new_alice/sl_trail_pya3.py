# subscribe ltp, it will be subscribed throughout the code
# then we have to place 2 orders ---> Sell ATM ce and ATM pe
# next, 
# we have to get the orderid of both 

# next,
# get their avg prices

# next,
# check if the orders are place sucessfuly & then
# place sl order for both,
# get the sl orders id

# next modify order after ltp changes every 50 points , move sl to 20 (rupees) points up!

api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"       
user_id = "285915"    
from time import sleep
import datetime as dt
from pya3 import *
alice = Aliceblue(user_id=user_id,api_key=api_key)
print(alice.get_session_id())

quantity = 25

LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []

def socket_open():  
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag: 
        alice.subscribe(subscribe_list)

def socket_close(): 
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message): 
    global LTP
    LTP = 0
    print("Error :", message)

def feed_data(message): 
    global LTP, subscribe_flag
    feed_message = json.loads(message)

    
    if feed_message["t"] == "ck":
        subscribe_flag = True
        pass
    elif feed_message["t"] == "tk":
        pass
    else:
        LTP = feed_message[
            'lp'] if 'lp' in feed_message else LTP  
        print(LTP)
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

while not socket_opened:
    pass

subscribe_list = [alice.get_instrument_by_symbol('INDICES', "NIFTY BANK")]
alice.subscribe(subscribe_list)
sleep(10)

def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)

bnf_nearest_strike = nearest_strike_bnf(LTP)

unsubscribe_list = [alice.get_instrument_by_symbol('INDICES', "NIFTY BANK")]
alice.subscribe(unsubscribe_list)


def latest_expiry():
    global datecalc, call
	
    call = False
    datecalc = dt.date.today().strftime("%d-%m-%Y") 
    while call == False:
        try:
            sleep(2)
            call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=int(39600), is_CE=True)
            print(call)
            if call['emsg'] =='No Data':
                datecalc = (dt.datetime.strptime(datecalc, "%d-%m-%Y")+  dt.timedelta(days=1)).strftime("%d-%m-%Y")
                call = False
            else:
                call = True
        except:
            pass

latest_expiry()
expiry_date = datecalc

bn_ce_trade = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=expiry_date, strike=bnf_nearest_strike, is_CE=True)
bn_pe_trade = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=expiry_date, strike=bnf_nearest_strike, is_CE=False)

def order_status(oid):
    order_details =alice.get_order_history(str(oid))
    order_status = order_details['Status']
    return order_status

def ap_generator(oid):
    order_details =alice.get_order_history(str(oid))
    avg_price = order_details['Avgprc']
    return avg_price

def get_oid(order_placed_output):
    oid = order_placed_output[0]['NOrdNo']
    return oid

# def get_avgp(number):
#     order_details = alice.get_order_history(number)
#     avgp = order_details['Avgprc']
#     return avgp


def sell_atm_options():
    global ce_sell_avg_price, pe_sell_avg_price, bnf_strike_before, tgp_bn_ce_sell, limit_price_ce, tgp_bn_pe_sell ,limit_price_pe
    bnf_strike_before = LTP
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
    
    ce_oid = get_oid(sell_call_order)
    pe_oid = get_oid(sell_put_order)
    
    ce_sell_avg_price =ap_generator(ce_oid) 
    pe_sell_avg_price =ap_generator(pe_oid)
    
    print('average price for call order is --> ',ce_sell_avg_price)
    print('average price for put order is --> ',pe_sell_avg_price)

    tgp_bn_ce_sell = (0.05* round((float(ce_sell_avg_price) + (float(ce_sell_avg_price))*0.20)/0.05))
    limit_price_ce = (0.05* round((float(tgp_bn_ce_sell) + 10)/0.05))

    # Stoploss PUT Details
    tgp_bn_pe_sell = (0.05* round((float(pe_sell_avg_price) + (float(pe_sell_avg_price))*0.20)/0.05))
    limit_price_pe = (0.05* round((float(tgp_bn_pe_sell) + 10)/0.05))


def place_sl_orders():
    global sl_ce_oid, sl_pe_oid
    
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
    
    sl_ce_oid = get_oid(sl_ce_order)
    sl_pe_oid = get_oid(sl_pe_order)
    
while dt.datetime.now().time() < dt.time(9,30):
    sleep(2)
try:
    sell_atm_options()
    place_sl_orders()
    print("Orders Placed Successfully!")
    
except Exception as e: 
    print(f"ERROR---->>>>{e}")



ce_avg_p = ce_sell_avg_price
pe_avg_p = pe_sell_avg_price
CE_SL_PRC = limit_price_ce
PE_SL_PRC = limit_price_pe

# runLoop = True
while dt.datetime.now().time() < dt.time(14,59,59):
    sleep(2)
    ce_data = alice.get_scrip_info(bn_ce_trade)
    pe_data = alice.get_scrip_info(bn_pe_trade)
    LTP_CE = int(ce_data['Ltp'])
    LTP_PE = int(pe_data['Ltp'])

    if int(LTP_CE - ce_avg_p) >=50:
        print("TIME TO MODIFY SLM CE ORDER TO 20 POINTS UP")
        mod_ce = alice.modify_order(transaction_type = TransactionType.Buy,
                     instrument = bn_ce_trade,
                      order_id=sl_ce_oid,
                                   quantity = quantity,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   price = (CE_SL_PRC + 20),
                                   trigger_price =(CE_SL_PRC + 30))
        ce_avg_p = ap_generator(sl_ce_oid)
        CE_SL_PRC += 20
        
            
    if int(LTP_PE - pe_avg_p) >=50:
        print("TIME TO MODIFY SLM PE ORDER TO 20 POINTS UP")
        mod_pe = alice.modify_order(transaction_type = TransactionType.Buy,
                     instrument = bn_pe_trade,
                      order_id=sl_pe_oid,
                                   quantity = quantity,
                                   order_type = OrderType.StopLossLimit,
                                   product_type = ProductType.Intraday,
                                   price = (PE_SL_PRC + 20),
                                   trigger_price =(PE_SL_PRC + 30),
                                   stop_loss = None,
                                   is_amo = False)
        pe_avg_p = ap_generator(sl_pe_oid)
        PE_SL_PRC += 20

