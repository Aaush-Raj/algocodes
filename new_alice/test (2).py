from alice_blue import *
import calendar
import datetime as dt
from time import sleep
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import smtplib
import sys
from pya3 import *
# import us_MA014

print("Time stamp: ",dt.datetime.now())

#Alice API

# client_code = us_MA014.client_code
# full_name = us_MA014.full_name
username = "285915"
# password = us_MA014.password
api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"
# twoFA = us_MA014.twoFA
user_gmail_id = 'aayushcontactinfo@gmail.com'
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
	global alice,socket_opened,username,password,twoFA,ltp_bnf,api_secret,bnf_call,order_placed,quantity
	try:
		net_margin = int(float(alice.get_balance()[0]["net"]))
		print("MARGIN AVAILABLE FOR TRADING IS ",net_margin)

		# if net_margin <= no_of_lots* 200000:
		# 	pass
		# else:
		# 	server = smtplib.SMTP('smtp.gmail.com',587)
		# 	server.starttls()
		# 	server.login(my_gmail_id,'ielyexucuxmibqem')
		# 	subject = "YOUR MARGIN IS LOW?"
		# 	body = """Dear Client,\nYour Margin is low for running the strategy. We request you to add margin.\nHappy Earning :)"""

		# 	msg = f'Subject: {subject}\n\n{body}'

		# 	server.sendmail(my_gmail_id,user_gmail_id,msg)
		# 	print('mail sent')
		# 	exit()

		subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
		alice.subscribe(subscribe_list)

		sleep(10)

		order_placed = False
		modify_order = False

		while dt.datetime.now().time() <= dt.time(9,19,55):
			print("time")
			sleep(10)

		while  order_placed == False:
			curr_ltp=int(float(ltp_bnf))
			print(curr_ltp)
			ce,pe = int(round(curr_ltp/100)*100),int(round(curr_ltp/100)*100)
			print('ATM CE ',ce,' ATM PE ',pe)
			unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
			alice.unsubscribe(unsubscribe_list)
			print("UNSUBSCRIBED")
			get_date_curr_expriry(ce)
			get_ce_curr_price(ce)
			get_pe_curr_price(pe)
			sleep(2)
			call_slm_order_placement()
			put_slm_order_placement()
			order_placed = True

	except Exception as e:
		print(f"some error occured at intial main:::>{e}")
		exception_type, exception_object, exception_traceback = sys.exc_info()
		line_number = exception_traceback.tb_lineno
		print("An error ocurred at Line number: ", line_number)
		
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.starttls()
		server.login(my_gmail_id,'ielyexucuxmibqem')
		subject = "Successfull ran for ", " ", " "
		body = """Script successfully ran for """, " ", " "

		msg = f'Subject: {subject}\n\n{body}'

		server.sendmail(my_gmail_id,my_gmail_id,msg)
		print('mail sent')
		exit()

def order_modify_call(number):
	order_details = alice.get_order_history(number)
	order_status = order_details['data'][0]['order_status']
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
			print("getting expiry date")
			call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=ce, is_CE=True)
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

	bnf_call = alice.get_instrument_for_fno(exch = 'NFO',symbol='NIFTY',expiry_date=datecalc,is_fut=False,strike=ce,is_CE=True)
	sell_ce_option(bnf_call)


def get_pe_curr_price(pe):
	print('get_pe_curr_price')
	global bnf_put

	bnf_put = alice.get_instrument_for_fno(exch = 'NFO',symbol='NIFTY',expiry_date=datecalc,is_fut=False,strike=pe,is_CE=False)
	sell_pe_option(bnf_put)

def sell_ce_option(bnf_call):
	global quantity,sell_order_call
	quantity=no_of_lots*int(bnf_call[5])
	sell_order_call = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	
def call_slm_order_placement():
	print("call_slm_order_placement")
	oid_call = sell_order_call['NOrdNo']
	call_order_details = alice.get_order_history(oid_call)
	global call_order_status,call_sell_avg_price
	call_order_status = call_order_details['Status']
	call_sell_avg_price = call_order_details['Avgprc']
	print("Sell Call order status is : ",call_order_status," with avg price ",call_sell_avg_price)
	if call_order_status == 'complete':
		slm_call_buy_price = 0.05 * round((float(call_sell_avg_price) * 1.20)/0.05)
		slm_limit_call_buy_price = float(round(slm_call_buy_price) + 10)
		sl_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_call_slm
		oid_call_slm = sl_order['NOrdNo']
		call_slm_order_details = alice.get_order_history(str(oid_call_slm)) 
		call_slm_order_status = call_slm_order_details['Status']
		print("Call SLM order placed with status:",call_slm_order_status)

def sell_pe_option(bnf_put):
	global quantity,sell_order_put
	quantity=no_of_lots*int(bnf_put[5])
	sell_order_put = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	
def put_slm_order_placement():
	print("put_slm_order_placement")
	oid_put = sell_order_put['NOrdNo']
	put_order_details = alice.get_order_history(oid_put)
	global put_order_status,put_sell_avg_price
	put_order_status = put_order_details['Status']
	put_sell_avg_price = put_order_details['Avgprc']
	print("Sell Put order status is: ",put_order_status," with avg price",put_sell_avg_price)
	if put_order_status == 'complete':
		slm_put_buy_price = 0.05 * round((float(put_sell_avg_price) * 1.20)/0.05)
		slm_limit_put_buy_price = float(round(slm_put_buy_price) + 10)
		sl_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_put_slm
		oid_put_slm = sl_order['NOrdNo']
		put_slm_order_details = alice.get_order_history(str(oid_put_slm))
		put_slm_order_status = put_slm_order_details['Status']
		print("Put SLM order places with status:",put_slm_order_status)


#Getting All the Necessary Variables

order_placed = False
modify_order = False
symbol = 'NIFTY BANK'
# no_of_lots = us_MA014.no_of_lots
bnf_script = alice.get_instrument_by_symbol('NSE',symbol)
socket_opened= False
NSE_holidays = [dt.date(2022, 10, 5),dt.date(2022, 10, 24),dt.date(2022, 10, 26),dt.date(2022, 11, 8),dt.date(2021, 11, 4),dt.date(2021, 11, 5),dt.date(2021, 11, 19)]

# starting main scrip

if (__name__=='__main__'):
	print('started straddle')

	if dt.date.today() in NSE_holidays:
		print('Enjoy!! its no trade today')
		sys.exit()
	main()
