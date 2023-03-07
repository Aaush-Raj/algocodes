from nsepython import *
from alice_blue import *
import calendar
import datetime as dt
import time
from time import sleep
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import smtplib
from datetime import date, datetime


api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"       
user_id = "285915"    

from pya3 import *
alice = Aliceblue(user_id=user_id,api_key=api_key)
print(alice.get_session_id())


LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []

def socket_open():  # Socket open callback function
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
        alice.subscribe(subscribe_list)

def socket_close():  # On Socket close this callback function will trigger
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global LTP
    LTP = 0
    print("Error :", message)

def feed_data(message):  # Socket feed data will receive in this callback function
    global ltp_bnf,LTP, subscribe_flag
	feed_message = json.loads(message)
	ltp_bnf = feed_message['lp']
	print(LTP)
    if feed_message["t"] == "ck":
        # print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
        subscribe_flag = True
        # print("subscribe_flag :", subscribe_flag)
        print("-------------------------------------------------------------------------------")
        pass
    elif feed_message["t"] == "tk":
        # print("Token Acknowledgement status :%s " % feed_message)
        ltp_bnf = feed_message['lp']
        print("-------------------------------------------------------------------------------")
        pass
    else:
        # print("Feed :", feed_message)
        LTP = feed_message['lp'] if 'lp' in feed_message else LTP # If LTP in the response it will store in LTP variable
		# print(feed_message['lp'] if 'lp' in feed_message else LTP)

# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

while not socket_opened:
    pass


# Connect the socket after socket close
# alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
#                       socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)



def main():
	global alice,socket_opened,username,password,twoFA,ltp_bnf,api_secret,bnf_call,order_placed,ce_price,pe_price,quantity

	subscribe_list = [alice.get_instrument_by_symbol('INDICES','NIFTY BANK')]
	alice.subscribe(subscribe_list)
	# alice.subscribe(bnf_script,LiveFeedType.COMPACT)
    
	sleep(10)

	order_placed = False
	modify_order = False


	while order_placed == False:

		curr_ltp=int(float(ltp_bnf))
		print(curr_ltp)
		print(type(curr_ltp))
		print(ltp_bnf)
		ce,pe = round(curr_ltp/100)*100,round(curr_ltp/100)*100
		print('ATM CE ',ce,' ATM PE ',pe)
		# ALICE.unsubscribe([ALICE.get_instrument_by_symbol("NSE", "NIFTY BANK")])
		# alice.stop_websocket()
		sleep(1)
		# ALICE.unsubscribe([alice.get_instrument_by_symbol("NSE", i) for i in ["NIFTY BANK"]])
		# alice.stop_websocket()
		unsubscribe_list = [alice.get_instrument_by_symbol('INDICES','NIFTY BANK')]
		alice.unsubscribe(unsubscribe_list)
		print("UNSUBSCRIBED")
		# ALICE.subscribe([ALICE.get_instrument_by_symbol("NSE", "NIFTY BANK")])

		get_date_curr_expriry()
		get_ce_curr_price(ce)
		get_pe_curr_price(pe)
		sleep(2)
		call_slm_order_placement()
		put_slm_order_placement()
		order_placed = True

	

def order_modify_call(number):
	order_details = alice.get_order_history(str(number))
	order_status = order_details['Status']
	print("call slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_call = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_call, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")

def order_modify_put(number):
	order_details = alice.get_order_history(str(number))
	order_status = order_details['Status']
	print("put slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_put = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_put, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")


def get_date_curr_expriry():
    called = None
    call = None
    exp_d = 0
    test = False
    date_today = date.today().strftime("%d-%m-%Y") 
    while called ==None:
        call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=date_today, strike=39600, is_CE=True)
        print(call)
        if test == False and call['emsg'] =='No Data':
            date_today = (datetime.strptime(date_today, "%d-%m-%Y")+  dt.timedelta(days=1)).strftime("%d-%m-%Y")
            x = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=date_today, strike=39600, is_CE=True)
            for i in x:
                if i == 25:
                    test = True
            
        else:
            called = True
            exp_d = date_today
            return exp_d
            break

datecalc =get_date_curr_expriry()
print("date--->",datecalc)






def get_ce_curr_price(ce):
	print('get_ce_curr_price')
	global bnf_call

	bnf_call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=ce, is_CE=True)

	sleep(1)
	ce_price=ltp_bnf
	print("%%%%%%%%%%%%%%%%%%%%",ce_price)
	print(ce_price)
	sell_ce_option(bnf_call,ce_price)





def get_pe_curr_price(pe):
	print('get_pe_curr_price')
	global bnf_put

	bnf_put = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=pe, is_CE=False)
	sleep(1)
	pe_price=ltp_bnf
	print(pe_price)
	sell_pe_option(bnf_put,pe_price)

def sell_ce_option(bnf_call,ce_price):
	global quantity,sell_order_call
	quantity=no_of_lots*int(bnf_call[5])
	sell_order_call = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	
def call_slm_order_placement():
	print("call_slm_order_placement")
	oid_call = sell_order_call[0]['NOrdNo']
	call_order_details = alice.get_order_history(str(oid_call))
	global call_order_status
	call_order_status = call_order_details['Status']
	call_sell_avg_price = call_order_details['Avgprc']
	print("Sell Call order status is : ",call_order_status," with avg price ",call_sell_avg_price)
	if call_order_status == 'complete':
		slm_call_buy_price = 0.05 * round((float(call_sell_avg_price) * 1.01)/0.05)
		slm_limit_call_buy_price = float(round(slm_call_buy_price + 10))
		sl_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_call_slm
		oid_call_slm = sl_order[0]['NOrdNo']
		call_slm_order_details = alice.get_order_history(str(oid_call_slm)) 
		call_slm_order_status = call_slm_order_details['Status']
		print("Call SLM order placed with status:",call_slm_order_status)

def sell_pe_option(bnf_put,pe_price):
	global quantity,sell_order_put
	quantity=no_of_lots*int(bnf_put[5])
	sell_order_put = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	
def put_slm_order_placement():
	print("put_slm_order_placement")
	oid_put = sell_order_put[0]['NOrdNo']
	put_order_details = alice.get_order_history(str(oid_put))
	global put_order_status
	put_order_status = put_order_details['Status']
	put_sell_avg_price = put_order_details['Avgprc']
	print("Sell Put order status is: ",put_order_status," with avg price",put_sell_avg_price)
	if put_order_status == 'complete':
		slm_put_buy_price = 0.05 * round((float(put_sell_avg_price) * 1.01)/0.05)
		slm_limit_put_buy_price = float(round(slm_put_buy_price + 10))
		sl_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_put_slm
		oid_put_slm = sl_order[0]['NOrdNo']
		put_slm_order_details = alice.get_order_history(str(oid_put_slm))
		put_slm_order_status = put_slm_order_details['Status']
		print("Put SLM order places with status:",put_slm_order_status)


#Getting All the Necessary Variables

order_placed = False
modify_order = False
symbol = 'Nifty Bank'
no_of_lots = 1
bnf_script = alice.get_instrument_by_symbol('NSE',symbol)
socket_opened= False


if (__name__=='__main__'):
	print('started straddle')
	main()

