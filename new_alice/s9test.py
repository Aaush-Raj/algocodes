from alice_blue import *
import calendar
import datetime as dt
from time import sleep
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import smtplib
import sys
# import us_HUF028
from pya3 import *

print("Time stamp: ",dt.datetime.now())

#Alice API
username = '285915'
api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'
#username = us_HUF028.username
# password = us_HUF028.password
# twoFA = us_HUF028.twoFA
# client_id = us_HUF028.client_id
#api_key = us_HUF028.api_key
strategy = "S8 FOUR LOT"
my_gmail_id = 'hiraninitin96@gmail.com'

alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())

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
#     ltp_bnf = feed_message['lp'] if 'lp' in feed_message else ltp_bnf
#     print(ltp_bnf)
    
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
        ltp_bnf = feed_message[
            'lp'] if 'lp' in feed_message else ltp_bnf  # If ltp_bnf in the response it will store in ltp_bnf variable
        print(ltp_bnf)
# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

while not socket_opened:
    pass

def main():
	global alice,socket_opened,username,password,twoFA,ltp_bnf,api_secret,bnf_call,order_placed,quantity
	try:

		subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
		alice.subscribe(subscribe_list)
		print("SUBSCRIBED LTP OF NIFTY")
		sleep(10)

		order_placed = False
		modify_order = False
		sl_to_cost = False

		while dt.datetime.now().time() <= dt.time(11,8,54):
			sleep(2)

		while order_placed == False:

			curr_ltp=int(float(ltp_bnf))
			print(curr_ltp)
			# ce,pe = int(round(curr_ltp/100)*100)-100,int(round(curr_ltp/100)*100)+100
			ce,pe = 18100,17900
			print('ATM CE ',ce,' ATM PE ',pe)
			unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
			alice.unsubscribe(unsubscribe_list)
			print("UNSUBSCRIBED LTP OF NIFTY")
			print("UNSUBSCRIBED")
			sleep(2)
			get_date_curr_expriry(ce)
			get_ce_curr_price(ce)
			get_pe_curr_price(pe)
			sleep(2)
			call_slm_order_placement()
			put_slm_order_placement()
			order_placed = True

		sleep(5)

		if order_status_function(oid_call) == 'rejected' and order_status_function(oid_put) == 'rejected':
			print("Both Ce and Pe order got rejected and so SL cost cannot be executed")
			exit()

		while True:

			if order_status_function(oid_call) == 'complete' or order_status_function(oid_put) == 'complete':
				tgt_sl_one_cancle_on_hit(oid_call,oid_put)
				if order_status_function(oid_call) == 'complete':
					call_slm_order_placement()
					break
				else:
					if order_status_function(oid_put) == 'complete':
						put_slm_order_placement()
						break
			time.sleep(10)

	except Exception as e:
		print(f"some error occured at intial main:::>{e}")
		error = f"{e}"
		exception_type, exception_object, exception_traceback = sys.exc_info()
		line_number = exception_traceback.tb_lineno
		print("An error ocurred at Line number: ", line_number)
		
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.starttls()
		server.login(my_gmail_id,'ielyexucuxmibqem')
		subject = "Error in cliend id:","user id:",username," ",strategy
		body = """Error below:\nError =""",error,"""\nLine number:""",line_number

		msg = f'Subject: {subject}\n\n{body}'

		server.sendmail(my_gmail_id,my_gmail_id,msg)
		print('mail sent')
		exit()

def modify_pe_order_to_cost(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	print("call slm order status",order_status)
	pe_sl_cost_price = 0.05 * round((float(put_sell_avg_price))/0.05)
	print(pe_sl_cost_price)
	modify_pe_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_put,order_id=number,quantity=quantity, order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday, price = pe_sl_cost_price + 10,trigger_price = pe_sl_cost_price)
	print(modify_pe_to_cost)

def modify_ce_order_to_cost(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	print("call slm order status",order_status)
	ce_sl_cost_price = 0.05 * round((float(call_sell_avg_price))/0.05)
	print(ce_sl_cost_price)
	modify_ce_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=bnf_call, order_id=number,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,  price = ce_sl_cost_price + 10,trigger_price = ce_sl_cost_price)
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
	order_status = order_details['data'][0]['order_status']
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
			# print("getting expiry date")
			call = alice.get_instrument_for_fno("NFO", "NIFTY", is_fut=False, expiry_date=datecalc, strike=ce, is_CE=True)
			print(call)
			if call['emsg'] =='No Data':
				# print('no data in call')
				datecalc = (dt.datetime.strptime(datecalc, "%Y-%m-%d")+  dt.timedelta(days=1)).strftime("%Y-%m-%d")
				call = False
			else:
				call = True
		except:
			pass

def get_ce_curr_price(ce):
	print('get_ce_curr_price')
	global bnf_call,ce_price

	bnf_call = alice.get_instrument_for_fno(exch = 'NFO',symbol='NIFTY',expiry_date=datecalc,is_fut=False,strike=int(ce),is_CE=True)
	print("$$$$$$$$$$$$$$",bnf_call)
	subscribe_list = [alice.get_instrument_for_fno(exch = 'NFO',symbol='NIFTY',expiry_date=datecalc,is_fut=False,strike=int(ce),is_CE=True)]
	alice.subscribe(subscribe_list)
	sleep(5)
	print("SUBSCRIBED CE NIFTY")
	ce_price=ltp_bnf
	print("CE PRICE ------------------->>>>",ce_price)

	sell_ce_option(bnf_call)
	unsubscribe_list = [bnf_call]
	print("UNSUBSCRIBED CE")

	alice.unsubscribe(unsubscribe_list)

def get_pe_curr_price(pe):
	print('get_pe_curr_price')
	global bnf_put,pe_price

	bnf_put = alice.get_instrument_for_fno(exch = 'NFO',symbol='NIFTY',expiry_date=datecalc,is_fut=False,strike=int(pe),is_CE=False)
	subscribe_list = [bnf_call]
	alice.subscribe(subscribe_list)
	pe_price=ltp_bnf

	print("PE PRICE ------------------->>>>",pe_price)
	sell_pe_option(bnf_put)
	unsubscribe_list = [bnf_call]

	alice.unsubscribe(unsubscribe_list)

def sell_ce_option(bnf_call):
	global quantity,sell_order_call
	quantity=no_of_lots*int(bnf_call[5])
	sell_order_call = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type = ProductType.Intraday,price = 0.05 * round((float(ce_price) * 1.35)/0.05)+1,trigger_price=0.05 * round((float(ce_price) * 1.35)/0.05),stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	print(sell_order_call)
	
def call_slm_order_placement():
	print("call_slm_order_placement")
	global oid_call,oid_call_slm
	oid_call = sell_order_call['NOrdNo']
	call_order_details = alice.get_order_history(oid_call)
	global call_order_status,call_sell_avg_price
	call_order_status = call_order_details['Status']
	call_sell_avg_price = call_order_details['Avgprc']
	print("Sell Call order status is : ",call_order_status," with avg price ",call_sell_avg_price)
	if call_order_status == 'complete':
		slm_call_buy_price = 0.05 * round((float(call_sell_avg_price) - 45)/0.05)
		slm_limit_call_buy_price = float(round(slm_call_buy_price) - 2)
		sl_order = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		
		oid_call_slm = sl_order['NOrdNo']
		call_slm_order_details = alice.get_order_history(oid_call_slm) 
		call_slm_order_status = call_slm_order_details['Status']
		print("Call SLM order placed with status:",call_slm_order_status)

		#target profit placement
		tgt_call_buy_price = 0.05 * round((float(call_sell_avg_price) + 100)/0.05)
		if tgt_call_buy_price < 1:
			tgt_call_buy_price = float(1)
		tgt_call_order = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Limit,product_type=ProductType.Intraday,price=tgt_call_buy_price,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_call_tgt
		oid_call_tgt = tgt_call_order['NOrdNo']
		call_tgt_order_details = alice.get_order_history(oid_call_tgt)
		call_tgt_order_status = call_tgt_order_details['Status']
		print("Call TGT order placed with status:",call_tgt_order_status)

	while True:
		if order_status_function(oid_call_slm) == 'complete' or order_status_function(oid_call_tgt) == 'complete':
			tgt_sl_one_cancle_on_hit(oid_call_slm,oid_call_tgt)
			print("PUT SL or TGT hit cancelling other side order")
			break

def sell_pe_option(bnf_put):
	global quantity,sell_order_put
	quantity=no_of_lots*int(bnf_put[5])
	sell_order_put = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	print(sell_order_put)
	
def put_slm_order_placement():
	print("put_slm_order_placement")
	global oid_put,oid_put_slm
	oid_put = sell_order_put['NOrdNo']
	put_order_details = alice.get_order_history(oid_put)
	global put_order_status,put_sell_avg_price
	put_order_status = put_order_details['Status']
	put_sell_avg_price = put_order_details['Avgprc']
	print("Sell Put order status is: ",put_order_status," with avg price",put_sell_avg_price)
	if put_order_status == 'complete':
		slm_put_buy_price = 0.05 * round((float(put_sell_avg_price) - 45)/0.05)
		slm_limit_put_buy_price = float(round(slm_put_buy_price) - 2)
		sl_order = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		oid_put_slm = sl_order['NOrdNo']
		put_slm_order_details = alice.get_order_history(oid_put_slm)
		put_slm_order_status = put_slm_order_details['Status']
		print("Put SLM order places with status:",put_slm_order_status)

		#target profit placement + status
		tgt_put_buy_price = 0.05 * round((float(put_sell_avg_price) + 100)/0.05)
		if tgt_put_buy_price < 1:
			tgt_put_buy_price = float(1)		
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
	order_status = order_details['Status']
	return(order_status)

def z_cancel_function(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['Status']
	token = order_status['token']
	alice.cancel_order(alice.get_instrument_by_token('NFO', token),number)
	print("order with number ",number,"is cancelled")

def tgt_sl_one_cancle_on_hit(number1,number2):

	print('loop started')

	if order_status_function(number1) == 'complete':
		z_cancel_function(number2)

	elif order_status_function(number2) == 'complete':
		z_cancel_function(number1)


#Getting All the Necessary Variables

order_placed = False
modify_order = False
symbol = 'NIFTY 50'
# no_of_lots = us_HUF028.no_of_lots_four_lot
no_of_lots = 2
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