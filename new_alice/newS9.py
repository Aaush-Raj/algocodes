# from nsepython import *
from pya3 import *
import calendar
import datetime as dt
import time
from time import sleep
# import us_HUF028
import sys


#Alice API
username = '285915'
api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'
# username = us_HUF028.username
# password = us_HUF028.password
# twoFA = us_HUF028.twoFA
# client_id = us_HUF028.client_id
# client_secret = us_HUF028.client_secret
# redirect_url = us_HUF028.redirect_url
# user_gmail_id = us_HUF028.user_gmail_id
# my_gmail_id = us_HUF028.my_gmail_id

# access_token = AliceBlue.login_and_get_access_token(username=username, password=password, twoFA=twoFA,  api_secret=client_secret, redirect_url=redirect_url, app_id=client_id)
# alice = AliceBlue(username=username, password=password, access_token=access_token,master_contracts_to_download=['NSE', 'BSE', 'NFO'])


alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())


#print(alice.get_balance()) # get balance / margin limits
#print(alice.get_profile()) # get profile
#print(alice.get_daywise_positions()) # get daywise positions
#print(alice.get_netwise_positions()) # get netwise positions
#print(alice.get_holding_positions()) # get holding positions

# defining fucntions 
ltp_bnf = 0
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
    global socket_opened, ltp_bnf
    socket_opened = False
    ltp_bnf = 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global ltp_bnf
    ltp_bnf = 0
    print("Error :", message)

def feed_data(message):  # Socket feed data will receive in this callback function
    global ltp_bnf, subscribe_flag
    feed_message = json.loads(message)
    
    if feed_message["t"] == "ck":
        subscribe_flag = True
        pass
    elif feed_message["t"] == "tk":
        pass
    else:
        ltp_bnf = feed_message[
            'lp'] if 'lp' in feed_message else ltp_bnf  # If ltp_bnf in the response it will store in ltp_bnf variable
        print(ltp_bnf)
# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

while not socket_opened:
    pass



def main():
	global alice,socket_opened,username,password,twoFA,ltp_bnf,api_secret,bnf_call,order_placed,ce_price,pe_price,quantity
	subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
	alice.subscribe(subscribe_list)
	sleep(10)

	# if socket_opened == False:
	# 	open_socket_now()

	# alice.subscribe(bnf_script,LiveFeedType.COMPACT)


	order_placed = False
	modify_order = False
	
	while dt.datetime.now().time()<= dt.time(11,8,51):
		sleep(10)
	try:
		while order_placed == False:
			print("LOOP")
			curr_ltp=float(ltp_bnf)
			ce,pe = int(round(curr_ltp/100)*100)-100,int(round(curr_ltp/100)*100)+100
			print('ATM CE ',ce,' ATM PE ',pe)
			print("WORKING")
			unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
			alice.unsubscribe(unsubscribe_list)

			get_date_curr_expriry(ce)
			get_ce_curr_price(ce)

			subscribe_list = [bnf_call]
			alice.subscribe(subscribe_list)
			sleep(5)
			print("SUBSCRIBED CALL")
			sleep(1)
			ce_price=ltp_bnf
			print(ce_price)
			sell_ce_option(bnf_call,ce_price)

			# alice.unsubscribe(bnf_call,LiveFeedType.COMPACT)
			unsubscribe_list = [bnf_call]
			alice.unsubscribe(unsubscribe_list)
			
			get_pe_curr_price(pe)
			sleep(1)
			order_placed = True

		sleep(2)

		if order_status_function(oid_call) == 'rejected' and order_status_function(oid_put) =='rejected':
			print("Both Ce and Pe order got rejected and so SL cost cannot be executed")
			sys.exit()

		while True:
			print("test ",dt.datetime.now().time())
			if order_status_function(oid_call) == 'complete' or order_status_function(oid_put) == 'complete':
				tgt_sl_one_cancle_on_hit(oid_call,oid_put)
				if order_status_function(oid_call) == 'complete':
					call_slm_order_placement()
					break
				else:
					if order_status_function(oid_put) == 'complete':
						put_slm_order_placement()
						break
			sleep(10)
			
	except Exception as e:
		error = f"Error:{e}"
		print(f"some error occured at intial main:::>{e}")
		exception_type, exception_object, exception_traceback = sys.exc_info()
		filename = exception_traceback.tb_frame.f_code.co_filename
		line_number = exception_traceback.tb_lineno
		print(line_number)
		# error_mail_sender(error)

# def error_mail_sender(error):
#     server = smtplib.SMTP('smtp.gmail.com',587)
#     server.starttls()
#     server.login(my_gmail_id,'ielyexucuxmibqem')
#     subject = "Script stopped because of an error for "+username
#     body = "script error ==>>" + error

#     msg = f'Subject: {subject}\n\n{body}'
#     server.sendmail(my_gmail_id,user_gmail_id,msg)
#     print('mail sent')

#Sir I am not working on this fnc as this is not being used anywhere now
def modify_pe_order_to_cost(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	print("call slm order status",order_status)
	pe_sl_cost_price = 0.05 * round((float(put_sell_avg_price))/0.05)
	modify_pe_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_put, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.StopLossLimit,quantity=quantity,price = pe_sl_cost_price + 10,trigger_price = pe_sl_cost_price)
	print(modify_pe_to_cost)

#Sir I am not working on this fnc as this is not being used anywhere now
def modify_ce_order_to_cost(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	print("call slm order status",order_status)
	ce_sl_cost_price = 0.05 * round((float(call_sell_avg_price))/0.05)
	modify_ce_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_call, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.StopLossLimit,quantity=quantity,price = ce_sl_cost_price + 10,trigger_price = ce_sl_cost_price)
	print(modify_ce_to_cost)

def order_modify_call(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	print("call slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_call = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_call, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")

def order_modify_put(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	print("put slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_put = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_put, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")

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

def get_ce_curr_price(ce):
	print('get_ce_curr_price')
	global bnf_call
	print(type(ce))
	bnf_call = alice.get_instrument_for_fno(exch="NFO",symbol='NIFTY',expiry_date=datecalc,is_fut=False,strike=ce,is_CE=True)
	# alice.subscribe(bnf_call,LiveFeedType.COMPACT)
	print(bnf_call)
	sleep(3)
	# subscribe_list = [bnf_call]
	# alice.subscribe(subscribe_list)
	# print("SUBSCRIBED CALL")
	# sleep(1)
	# ce_price=ltp_bnf
	# print(ce_price)
	# sell_ce_option(bnf_call,ce_price)

	# # alice.unsubscribe(bnf_call,LiveFeedType.COMPACT)
	# unsubscribe_list = [bnf_call]
	# alice.unsubscribe(unsubscribe_list)
	# print("UNSUBSCRIBED CALL")
	# alice.unsubscribe(subscribe_list)

def get_pe_curr_price(pe):
	print('get_pe_curr_price')
	global bnf_put

	bnf_put = alice.get_instrument_for_fno(exch="NFO",symbol='NIFTY',expiry_date=datecalc,is_fut=False,strike=pe,is_CE=False)
	# alice.subscribe(bnf_put,LiveFeedType.COMPACT)
	subscribe_list = [bnf_put]
	alice.subscribe(subscribe_list)
	sleep(1)
	pe_price=ltp_bnf
	sell_pe_option(bnf_put,pe_price)

	# alice.unsubscribe(bnf_put,LiveFeedType.COMPACT)
	unsubscribe_list = [bnf_put]
	alice.unsubscribe(unsubscribe_list)


def sell_ce_option(bnf_call,ce_price):
	global quantity,sell_order_call,oid_call
	quantity=no_of_lots*int(bnf_call[5])
	sell_order_call = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type = ProductType.Intraday,price = 0.05 * round(((float(ce_price) * 1.35)/0.05)+ 1),trigger_price=0.05 * round((float(ce_price) * 1.35)/0.05) ,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	oid_call = sell_order_call['NOrdNo']
	
def call_slm_order_placement():
	print("call_slm_order_placement")
	# oid_call = sell_order_call['NOrdNo'] #this line not needed
	call_order_details = alice.get_order_history(oid_call)
	global call_order_status,call_sell_avg_price
	call_order_status = call_order_details['Status']
	call_sell_avg_price = call_order_details['Avgprc']
	print("Sell Call order status is : ",call_order_status," with avg price ",call_sell_avg_price)
	if call_order_status == 'complete':
		#slm order placement + its status
		slm_call_buy_price = 0.05 * round((float(call_sell_avg_price) - 45)/0.05)
		slm_limit_call_buy_price = float(round(float(slm_call_buy_price) - 2))
		sl_order = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_call_slm
		oid_call_slm = sl_order['NOrdNo']
		call_slm_order_details = alice.get_order_history(oid_call_slm)
		call_slm_order_status = call_slm_order_details['Status']
		print("Call SLM order placed with status:",call_slm_order_status)

		#target profit placement
		tgt_call_buy_price = 0.05 * round((float(call_sell_avg_price) + 80)/0.05)
		tgt_call_order_ = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Limit,product_type=ProductType.Intraday,price=tgt_call_buy_price,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_call_tgt
		oid_call_tgt = tgt_call_order_['NOrdNo']
		call_tgt_order_details = alice.get_order_history(oid_call_tgt)
		call_tgt_order_status = call_tgt_order_details['Status']
		print("Call TGT order placed with status:",call_tgt_order_status)

	while True:
		if order_status_function(oid_call_slm) == 'complete' or order_status_function(oid_call_tgt) == 'complete':
			tgt_sl_one_cancle_on_hit(oid_call_slm,oid_call_tgt)
			print("PUT SL or TGT hit cancelling other side order")
			break

def sell_pe_option(bnf_put,pe_price):
	global quantity,sell_order_put,oid_put
	quantity=no_of_lots*int(bnf_put[5])
	sell_order_put = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type = ProductType.Intraday,price = 0.05 * round((float(pe_price) * 1.35)/0.05) + 1,trigger_price= 0.05 * round((float(pe_price) * 1.35)/0.05),stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	oid_put = sell_order_put['NOrdNo']
	
def put_slm_order_placement():
	print("put_slm_order_placement")
	# oid_put = sell_order_put['data']['oms_order_id'] #code not needed
	put_order_details = alice.get_order_history(oid_put)
	global put_order_status,put_sell_avg_price
	put_order_status = put_order_details['Status']
	put_sell_avg_price = put_order_details['Avgprc']
	print("Sell Put order status is: ",put_order_status," with avg price",put_sell_avg_price)
	if put_order_status == 'complete':
		#TGT order placement + its status
		slm_put_buy_price = 0.05 * round((float(put_sell_avg_price) - 45 )/0.05)
		slm_limit_put_buy_price = float(round(float(slm_put_buy_price) - 2))
		sl_order = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_put_slm
		oid_put_slm = sl_order['NOrdNo']
		put_slm_order_details = alice.get_order_history(oid_put_slm)
		put_slm_order_status = put_slm_order_details['Status']
		print("Put SLM order places with status:",put_slm_order_status)

		#target profit placement + status
		tgt_put_buy_price = 0.05 * round((float(put_sell_avg_price) + 80)/0.05)
		tgt_put_order = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.Limit,product_type=ProductType.Intraday,price=tgt_put_buy_price,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_put_tgt
		oid_put_tgt = tgt_put_order['NOrdNo']
		put_tgt_order_details = alice.get_order_history(oid_put_tgt)
		put_tgt_order_status = put_tgt_order_details['Status']
		print("Put TGT order placed with status:",put_tgt_order_status)

	while True:
		if order_status_function(oid_put_slm) == 'complete' or order_status_function(oid_put_tgt) == 'complete':
			tgt_sl_one_cancle_on_hit(oid_put_slm,oid_put_tgt)
			print("PUT SL or TGT hit cancelling other side order")
			break

def order_status_function(number):
	order_status= None
	order_details = alice.get_order_history(number)
	order_status =  order_details['Status']
	return(order_status)

def cancel_order(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	if order_status == "trigger pending":
		alice.cancel_order(number)
		print("order with number ",number,"is cancelled")
	else:
		print("order is already executed")

def tgt_sl_one_cancle_on_hit(number1,number2):

	print('loop started')

	if order_status_function(number1) == 'complete':
		alice.cancel_order(number2)

	elif order_status_function(number2) == 'complete':
		alice.cancel_order(number1)


#Getting All the Necessary Variables

order_placed = False
modify_order = False
symbol = 'Nifty 50'
no_of_lots = 1
bnf_script = alice.get_instrument_by_symbol('NSE',symbol)
socket_opened= False
NSE_holidays = [dt.date(2021, 7, 21),dt.date(2021, 8, 19),dt.date(2021, 9, 10),dt.date(2021, 10, 15),dt.date(2021, 11, 4),dt.date(2021, 11, 5),dt.date(2021, 11, 19)]

# starting main scrip

if (__name__=='__main__'):
	print('started straddle')

	if dt.date.today() in NSE_holidays:
		print('Enjoy!! its no trade today')
		sys.exit()
	main()