import sys
import math
import time
import datetime as dt
from time import sleep
from datetime import date,timedelta,datetime
from pya3 import *

api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"       
user_id = "285915"    
alice = Aliceblue(user_id=user_id,api_key=api_key)
print(alice.get_session_id())


def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)
def strGreen(skk):return "\033[92m {}\033[00m".format(skk)
def strRed(skk):return "\033[91m {}\033[00m".format(skk)


symbol = 'Nifty Bank'
bnf_script = alice.get_instrument_by_symbol('NSE', symbol)

socket_opened = False

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


def order_status(oid):
    order_details =alice.get_order_history(str(oid))
    order_status = order_details['Status']
    return order_status

def ap_generator(oid):
    order_details =alice.get_order_history(str(oid))
    avg_price = order_details['Avgprc']
    return avg_price


def sell_atm_options():
    global ce_sell_avg_price, pe_sell_avg_price,bn_ce_sell_order_id, bn_pe_sell_order_id
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
    
    bn_ce_sell_order_id = sell_call_order[0]['NOrdNo']
    bn_pe_sell_order_id = sell_put_order[0]['NOrdNo']
    ce_sell_avg_price =ap_generator(bn_ce_sell_order_id) 
    pe_sell_avg_price =ap_generator(bn_pe_sell_order_id)
    
    print("%%%%--- ORDER complete----%%%%",sell_call_order,sell_put_order)
   

def stoploss_order():
    print("STOPLOSS FUNCTION STARTED")
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
    global sl_ce_oid,sl_pe_oid
    sl_ce_oid = sl_ce_order[0]['NOrdNo']
    sl_pe_oid = sl_pe_order[0]['NOrdNo']

    print("%%%% STOPLOSS ORDERS complete SUCCESSFULLY %%%%",sl_ce_order,sl_pe_order)
    print("CALL ORDER SL DETAILS--> Limit price is",strGreen(limit_price_ce),"and Trigger price is",strGreen(tgp_bn_ce_sell))
    print("PUT ORDER SL DETAILS--> Limit price is",strGreen(limit_price_pe),"and Trigger price is",strGreen(tgp_bn_pe_sell))
    
    

def target_orders():
    global tgt_ce_oid,tgt_pe_oid
    
    ce_target_order = alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = bn_ce_trade,
                     quantity = quantity,
                     order_type = OrderType.Limit,
                     product_type = ProductType.Intraday,
                     price = target_ce_price,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
    
    pe_target_order = alice.place_order(transaction_type = TransactionType.Buy,
                 instrument = bn_pe_trade,
                 quantity = quantity,
                 order_type = OrderType.Limit,
                 product_type = ProductType.Intraday,
                 price = target_pe_price,
                 trigger_price = None, 
                 stop_loss = None,
                 square_off = None,
                 trailing_sl = None,
                 is_amo = False)
    
    print("Target for CALL Order is",strGreen(target_ce_price),"and Target for PUT Order is",strGreen(target_pe_price))
    tgt_ce_oid = ce_target_order[0]['NOrdNo']
    tgt_pe_oid = pe_target_order[0]['NOrdNo']
    

    
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
    
def get_ltp(ltp):
    global ltp_BN
    ltp_BN = ltp
    print(ltp)
    return ltp


def main():
        
    subscribe_list = [alice.get_instrument_by_symbol('INDICES', "NIFTY BANK")]
    alice.subscribe(subscribe_list)
    sleep(10)

    order_complete = False
    while dt.datetime.now().time() < dt.time(8,20):
        print("wait for the time to be 9:20 ; Right now the time is only -->)",dt.datetime.now().time())
        sleep(5)
    try:
        lot_size = 1
        quantity = lot_size*(25) 
        # try:

        print(LTP)
        print(LTP)
        bnf_nearest_strike = nearest_strike_bnf(float(LTP))
        latest_expiry()
        expiry_date = latest_expiry()
        expiry_date = datecalc
        print("----------------------->>>>>>>>>>>>>>>>>>>")
        print(expiry_date)

        print("Lot size =" ,strGreen(lot_size) , "and Quantity = " ,strGreen(quantity))
        print("Latest expiry is on", strGreen(expiry_date))

        bn_100_above_strike = bnf_nearest_strike + 100
        bn_100_below_strike = bnf_nearest_strike - 100
        print("banknifty LTP is ",strGreen(LTP))
        print("NEAREST STRIKE PRICE OF BANKNIFTY IS",strGreen(bnf_nearest_strike))
        unsubscribe_list = [alice.get_instrument_by_symbol('INDICES','NIFTY BANK')]
        alice.unsubscribe(unsubscribe_list)

        bn_ce_trade = alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
        bn_pe_trade = alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=bnf_nearest_strike, is_CE=False)
        
        sell_atm_options()
        
        # Stoploss CALL Details
        tgp_bn_ce_sell = (0.05* round((float(ce_sell_avg_price) + (float(ce_sell_avg_price))*0.20)/0.05))
        limit_price_ce = (0.05* round((float(tgp_bn_ce_sell) + 10)/0.05))

        # Stoploss PUT Details
        tgp_bn_pe_sell = (0.05* round((float(pe_sell_avg_price) + (float(pe_sell_avg_price))*0.20)/0.05))
        limit_price_pe = (0.05* round((float(tgp_bn_pe_sell) + 10)/0.05))
        #Target Order details
        target_ce_price = (0.05* round((float(ce_sell_avg_price) - (float(ce_sell_avg_price)*0.50))/0.05))
        target_pe_price = (0.05* round((float(pe_sell_avg_price) - (float(pe_sell_avg_price)*0.50))/0.05))
        
        if order_status(bn_ce_sell_order_id) == "rejected" and order_status(bn_pe_sell_order_id) == "rejected":
            print(strRed("Orders are rejected so Stoploss orders won't be complete, Please try again."))
            sys.exit(0) 
        else:
            stoploss_order()
            target_orders()
    
        print(strGreen("All Orders complete Successfully! Now Just wait till 3:10PM. "))

    except Exception as e:
        print(strRed(f"ERROR---->>>>{e}"))
        
        
        
    
    # except Exception as e:
    #     print(strRed(f"ERROR---->>>>{e}"))
        
        
        
        
    # logic to be running till closing time
    while dt.datetime.now().time() < dt.time(15,10):
        sleep(5)
        print("WHILE LOOP RUNNING")

        if order_status(sl_ce_oid) =='complete':
            token = alice.get_order_history(tgt_ce_oid)['token']
            alice.cancel_order(alice.get_instrument_by_token('NFO', token),tgt_ce_oid)
            alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_pe_trade, quantity=quantity, product_type=ProductType.Intraday, order_id=str(sl_pe_oid), order_type = OrderType.StopLossLimit,price = int(pe_sell_avg_price + 10),trigger_price =pe_sell_avg_price)
            break

        if order_status(sl_pe_oid) =='complete':
            token = alice.get_order_history(tgt_pe_oid)['token']
            alice.cancel_order(alice.get_instrument_by_token('NFO', token),tgt_ce_oid)
            alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_ce_trade, quantity=quantity, product_type=ProductType.Intraday, order_id=str(sl_ce_oid), order_type = OrderType.StopLossLimit,price = int(ce_sell_avg_price + 10),trigger_price =ce_sell_avg_price )
            break

        if order_status(tgt_ce_oid) == 'complete':
            token = alice.get_order_history(sl_ce_oid)['token']
            alice.cancel_order(alice.get_instrument_by_token('NFO', token),sl_ce_oid)
            break   
            
        if order_status(tgt_pe_oid) == 'complete':
            token = alice.get_order_history(sl_pe_oid)['token']
            alice.cancel_order(alice.get_instrument_by_token('NFO', token),sl_pe_oid)
            break
            
        else:
            pass
        
    #EXIT ORDER LOGIC
    while dt.datetime.now().time() < dt.time(15,10):
        print("wait for the time to be 15:10 ; Right now the time is only -->)",datetime.datetime.now().time())
        time.sleep(5)
    try:
        exit_orders()
        print("DONE FOR THE DAY, HOPE YOU MADE GOOD PROFIT.")
        
    except Exception as e:
        print(strRed(f"ERROR---->>>>{e}"))


#doubts --> see the cancel order code from repo and check the Float and round values of Limit and sl price

if (__name__=='__main__'):
    print('started straddle')
	main()

	# if dt.date.today() in NSE_holidays:
	# 	print('Enjoy!! its no trade today')
	# 	sys.exit()