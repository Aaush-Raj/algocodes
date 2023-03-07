from alice_blue import *
import calendar
import datetime as dt
from time import sleep
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import smtplib
import sys
# import us_402855
from pya3 import *
#Alice API

#Alice API

# username = us_402855.username
# password = us_402855.password
# twoFA = us_402855.twoFA
# client_id = us_402855.client_id
# client_secret = us_402855.client_secret
# redirect_url = us_402855.redirect_url
# api_key = us_402855.api_key
strategy = "S1 THREE LOT"
username = '285915'
api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'
alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())


ltp_nf = 0
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
    global socket_opened, ltp_nf
    socket_opened = False
    ltp_nf = 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global ltp_nf
    ltp_nf = 0
    print("Error :", message)

def feed_data(message):  # Socket feed data will receive in this callback function
    global ltp_nf, subscribe_flag
    feed_message = json.loads(message)
#     ltp_nf = feed_message['lp'] if 'lp' in feed_message else ltp_nf
#     print(ltp_nf)
    
    if feed_message["t"] == "ck":
#         print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
        subscribe_flag = True
#         print("subscribe_flag :", subscribe_flag)
        pass
    elif feed_message["t"] == "tk":
#         print("Token Acknowledgement status :%s " % feed_message)
#         print("-------------------------------------------------------------------------------")
        pass
    else:
#         print("Feed :", feed_message)
        ltp_nf = feed_message[
            'lp'] if 'lp' in feed_message else ltp_nf  # If ltp_nf in the response it will store in ltp_bnf variable
        print(ltp_nf)
# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

while not socket_opened:
    pass

def main():
	global alice,socket_opened,username,password,twoFA,api_secret,order_placed,quantity,script,expiry_days,days_to_jump,symbol,nf_script,no_of_lots

	symbol = 'Nifty 50'

	nf_script = alice.get_instrument_by_symbol('NSE',symbol)

	subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
	alice.subscribe(subscribe_list)

	ltp_nf = 17600

	get_date_curr_expriry(ltp_nf)

	#### INPUT CRITERIA #####

	no_of_lots = 1
	

	if_LPH = True

	lph = 17177
	lpl = 0

	days_to_jump = 1

	####################

	quantity = 50*no_of_lots

	order_placed = False

	script = "NIFTY"

	fetch_mon_ex_dt()

	instrument_to_trade = alice.get_instrument_for_fno(exch="NFO", symbol =  "NIFTY",expiry_date=str(mon_ex_date), is_fut=True,strike=None,is_CE = False)

	if if_LPH == True:
		while float(ltp_nf) < lph:
			print("wait for LPH break")
			sleep(2)
		try:
			while order_placed == False:
				buy_future = alice.place_order(transaction_type=TransactionType.Buy,instrument=instrument_to_trade,quantity=no_of_lots * 50,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
				#hedge_buy()
				unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
				alice.unsubscribe(unsubscribe_list)
				nearest_stk = int(round(ltp_nf/50)*50)
				
				hedge_type = 'pe'
				get_hedge_ins(nearest_stk,hedge_type)
				


		except Exception as e:
			print(f"some error occured at intial main:::>{e}")

	elif if_LPH == False:
		while ltp_nf > lpl:
			print("wait for LPL break")
			sleep(2)
		try:
			while order_placed == False:
				sell_future = alice.place_order(transaction_type=TransactionType.Sell,instrument=instrument_to_trade,quantity=no_of_lots * 50,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
				#hedge_buy()
				unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
				alice.unsubscribe(unsubscribe_list)

		except Exception as e:
			print(f"some error occured at intial main:::>{e}")



def get_hedge_ins(ltp,hedge_type):
	if hedge_type == 'ce':
		ord_type = True
	else:	
		ord_type = False


	new_stk = ltp - 400
	print(new_stk)
	run_loop = True
	while run_loop == True:
		print("LOOP")
		print(datecalc)
		z = alice.get_scrip_info(alice.get_instrument_for_fno(exch="NFO",symbol='NIFTY', expiry_date=datecalc, is_fut=False,strike=new_stk, is_CE=ord_type))
		strike_ltp = z['LTP']
		print(strike_ltp)
		print("strike-> ",new_stk,"Ltp->",strike_ltp)
		sleep(1)
		
		if float(strike_ltp) < 15:
			print("WE GOT OUR STRIKE")
			run_loop = False
			print(ord_type)
			instrument =  alice.get_instrument_for_fno(exch="NFO",symbol='NIFTY', expiry_date=datecalc, is_fut=False,strike=new_stk, is_CE=ord_type)
			print("YES")
			print(instrument)
			buy_hedge = alice.place_order(transaction_type = TransactionType.Buy,instrument = instrument,quantity = quantity,order_type = OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price = None,stop_loss = None,square_off = None,trailing_sl = None,is_amo = False)

			return buy_hedge
			break
			
		else:
			print("STRIKE NOT FOUND")
			new_stk -= 50



def get_date_curr_expriry(ce):
	print('date_curr_expiry')
	global datecalc, call

	call = False
	datecalc = dt.date.today().strftime("%Y-%m-%d") 
	while call == False:
		try:
			print("getting expiry date")
			call = alice.get_instrument_for_fno("NFO", "NIFTY", is_fut=False, expiry_date=datecalc, strike=ce, is_CE=True)
			print(call)
			if call['emsg'] =='No Data':
				print('no data in call')
				datecalc = (dt.datetime.strptime(datecalc, "%Y-%m-%d")+  dt.timedelta(days=1)).strftime("%Y-%m-%d")
				call = False
			else:
				call = True
		except:
			pass


def fetch_mon_ex_dt():
    print('fetch_mon_ex_dt')
    global mon_ex_date,days_to_jump
    nf_fut = False
    mon_ex_date = dt.date.today() + dt.timedelta(days=1)
    while nf_fut == False:
        try:
            print("getting expiry date")
            nf_fut = alice.get_instrument_for_fno(exch="NFO", symbol =  "NIFTY",expiry_date=str(mon_ex_date), is_fut=True,strike=None,is_CE = False)
            if nf_fut['emsg'] =='No Data':

                mon_ex_date = mon_ex_date   + dt.timedelta(days = 1)
                nf_fut = False
            else:
                call = True

        except:
            pass

def get_pe_curr_price(pe):
	print('get_pe_curr_price')
	global nf_put

	nf_put = alice.get_instrument_for_fno(symbol='NIFTY',expiry_date=mon_ex_date,is_fut=False,strike=pe,is_CE=False)
	nf_hedge_put = alice.get_instrument_for_fno(symbol='NIFTY',expiry_date=rec_ex_date,is_fut=False,strike=pe - 400,is_CE=False)
	alice.subscribe(nf_put,LiveFeedType.COMPACT)
	sleep(1)
	pe_price=ltp_nf
	sell_pe_option(nf_put,pe_price)

	alice.unsubscribe(nf_put,LiveFeedType.COMPACT)

def sell_pe_option(nf_put,pe_price):
	global quantity,sell_order_put
	quantity=no_of_lots*int(nf_put[5])
	sell_order_put = alice.place_order(transaction_type=TransactionType.Sell,instrument=nf_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	buy_order_put = alice.place_order(transaction_type=TransactionType.Buy,instrument=nf_hedge_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

def get_ce_curr_price(ce):
	print('get_ce_curr_price')
	global nf_call

	nf_call = alice.get_instrument_for_fno(symbol='NIFTY',expiry_date=mon_ex_date,is_fut=False,strike=ce,is_CE=False)
	nf_hedge_call = alice.get_instrument_for_fno(symbol='NIFTY',expiry_date=rec_ex_date,is_fut=False,strike=ce - 400,is_CE=False)
	alice.subscribe(nf_call,LiveFeedType.COMPACT)
	sleep(1)
	ce_price=ltp_nf
	sell_ce_option(nf_call,ce_price)

	alice.unsubscribe(nf_call,LiveFeedType.COMPACT)

def sell_ce_option(nf_call,ce_price):
	global quantity,sell_order_call
	quantity=no_of_lots*int(nf_call[5])
	sell_order_call = alice.place_order(transaction_type=TransactionType.Sell,instrument=nf_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	buy_order_call = alice.place_order(transaction_type=TransactionType.Buy,instrument=nf_hedge_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

if (__name__=='__main__'):
	print('start')
	main()
