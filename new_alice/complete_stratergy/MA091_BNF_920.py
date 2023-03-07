from nsepython import *
from alice_blue import *
import calendar
import datetime as dt
import time
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import smtplib

#V10
# starting of script

print("Bank Nifty 920 Straddle bot started for . Time stamp: ",datetime.datetime.now())

#Alice API

client_code = ''
full_name = ''
username = ''
password = ''
twoFA = ''
client_id = ''
client_secret = ''
redirect_url = 'https://ant.aliceblueonline.com/plugin/callback'
user_gmail_id = ''
my_gmail_id = ''

access_token = AliceBlue.login_and_get_access_token(username=username, password=password, twoFA=twoFA,  api_secret=client_secret, redirect_url=redirect_url, app_id=client_id)
alice = AliceBlue(username=username, password=password, access_token=access_token,master_contracts_to_download=['NSE', 'BSE', 'NFO'])

#print(alice.get_balance()) # get balance / margin limits
#print(alice.get_profile()) # get profile
#print(alice.get_daywise_positions()) # get daywise positions
#print(alice.get_netwise_positions()) # get netwise positions
#print(alice.get_holding_positions()) # get holding positions

# defining fucntions 

def event_handler_quote_update(message):
	global ltp_bnf
	ltp_bnf = message['ltp']
	print('LTP OF BANKNIFTY IS:',ltp_bnf)

def open_callback():
	global socket_opened
	socket_opened = True

def open_socket_now():
	global socket_opened

	socket_opened = False
	alice.start_websocket(subscribe_callback = event_handler_quote_update,socket_open_callback=open_callback,run_in_background = True)

	time.sleep(10)

	while (socket_opened==False):  #wait till socket open & then subscribe
		pass

def main():
	global alice,socket_opened,username,password,twoFA,ltp_bnf,api_secret,bnf_call,order_placed,ce_price,pe_price,quantity

	net_margin = float(alice.get_balance()['data']['cash_positions'][0]['net'])
	print("MARGIN AVAILABLE FOR TRADING IS ",net_margin)

	if net_margin >= no_of_lots* 200000:
		pass
	else:
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.starttls()
		server.login(my_gmail_id,'')
		subject = "YOUR MARGIN IS LOW?"
		body = """Dear Client,

Your Margin is low for running the strategy. We request you to add margin.

Happy Earning :)"""

		msg = f'Subject: {subject}\n\n{body}'

		server.sendmail(my_gmail_id,user_gmail_id,msg)
		print('mail sent')
		exit()
			
	if socket_opened == False:
		open_socket_now()

	alice.subscribe(bnf_script,LiveFeedType.COMPACT)
	time.sleep(10)

	order_placed = False
	modify_order = False

	while datetime.datetime.now().time()<= datetime.time(9,19,50):
		time.sleep(10)
	try:
		while order_placed == False:

			curr_ltp=ltp_bnf
			ce,pe = int(round(curr_ltp/100)*100),int(round(curr_ltp/100)*100)
			print('ATM CE ',ce,' ATM PE ',pe)
			alice.unsubscribe(bnf_script,LiveFeedType.COMPACT)
			get_date_curr_expriry(ce)
			get_ce_curr_price(ce)
			get_pe_curr_price(pe)
			time.sleep(2)
			call_slm_order_placement()
			put_slm_order_placement()
			order_placed = True

	except Exception as e:
		print(f"some error occured at intial main:::>{e}")

	server = smtplib.SMTP('smtp.gmail.com',587)
	server.starttls()
	server.login(my_gmail_id,'')
	subject = "Successfull ran for ", client_code, " ", username, " ", full_name
	body = """Script successfully ran for """, client_code, " ", username, " ", full_name

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
	global datecalc
	print('ATM CE is: ',ce)
	call = None
	datecalc = dt.date.today()
	# get current week expiry date
	while call == None:
		try:
			call = alice.get_instrument_for_fno(symbol='BANKNIFTY',expiry_date=datecalc, is_fut=False,strike=ce,is_CE = True)
			if call == None:
				print('No value in call')

				datecalc = datecalc	+ dt.timedelta(days = 1)

		except:
			pass

def get_ce_curr_price(ce):
	print('get_ce_curr_price')
	global bnf_call

	bnf_call = alice.get_instrument_for_fno(symbol='BANKNIFTY',expiry_date=datecalc,is_fut=False,strike=ce,is_CE=True)
	alice.subscribe(bnf_call,LiveFeedType.COMPACT)
	time.sleep(1)
	ce_price=ltp_bnf
	sell_ce_option(bnf_call,ce_price)

	alice.unsubscribe(bnf_call,LiveFeedType.COMPACT)

def get_pe_curr_price(pe):
	print('get_pe_curr_price')
	global bnf_put

	bnf_put = alice.get_instrument_for_fno(symbol='BANKNIFTY',expiry_date=datecalc,is_fut=False,strike=pe,is_CE=False)
	alice.subscribe(bnf_put,LiveFeedType.COMPACT)
	time.sleep(1)
	pe_price=ltp_bnf
	sell_pe_option(bnf_put,pe_price)

	alice.unsubscribe(bnf_put,LiveFeedType.COMPACT)


def sell_ce_option(bnf_call,ce_price):
	global quantity,sell_order_call
	quantity=no_of_lots*int(bnf_call[5])
	sell_order_call = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	
def call_slm_order_placement():
	print("call_slm_order_placement")
	oid_call = sell_order_call['data']['oms_order_id']
	call_order_details = alice.get_order_history(int(oid_call))
	global call_order_status
	call_order_status = call_order_details['data'][0]['order_status']
	call_sell_avg_price = call_order_details['data'][0]['average_price']
	print("Sell Call order status is : ",call_order_status," with avg price ",call_sell_avg_price)
	if call_order_status == 'complete':
		slm_call_buy_price = 0.05 * round((call_sell_avg_price * 1.20)/0.05)
		slm_limit_call_buy_price = float(round(slm_call_buy_price + 10))
		sl_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_call_slm
		oid_call_slm = sl_order['data']['oms_order_id']
		call_slm_order_details = alice.get_order_history(int(oid_call_slm)) 
		call_slm_order_status = call_slm_order_details['data'][0]['order_status']
		print("Call SLM order placed with status:",call_slm_order_status)

def sell_pe_option(bnf_put,pe_price):
	global quantity,sell_order_put
	quantity=no_of_lots*int(bnf_put[5])
	sell_order_put = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
	
def put_slm_order_placement():
	print("put_slm_order_placement")
	oid_put = sell_order_put['data']['oms_order_id']
	put_order_details = alice.get_order_history(oid_put)
	global put_order_status
	put_order_status = put_order_details['data'][0]['order_status']
	put_sell_avg_price = put_order_details['data'][0]['average_price']
	print("Sell Put order status is: ",put_order_status," with avg price",put_sell_avg_price)
	if put_order_status == 'complete':
		slm_put_buy_price = 0.05 * round((put_sell_avg_price * 1.20)/0.05)
		slm_limit_put_buy_price = float(round(slm_put_buy_price + 10))
		sl_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
		global oid_put_slm
		oid_put_slm = sl_order['data']['oms_order_id']
		put_slm_order_details = alice.get_order_history(oid_put_slm)
		put_slm_order_status = put_slm_order_details['data'][0]['order_status']
		print("Put SLM order places with status:",put_slm_order_status)


#Getting All the Necessary Variables

order_placed = False
modify_order = False
symbol = 'Nifty Bank'
no_of_lots = 2
bnf_script = alice.get_instrument_by_symbol('NSE',symbol)
socket_opened= False
NSE_holidays = [datetime.date(2021, 7, 21),datetime.date(2021, 8, 19),datetime.date(2021, 9, 10),datetime.date(2021, 10, 15),datetime.date(2021, 11, 4),datetime.date(2021, 11, 5),datetime.date(2021, 11, 19)]

# starting main scrip

if (__name__=='__main__'):
	print('started straddle')

	if datetime.date.today() in NSE_holidays:
		print('Enjoy!! its no trade today')
		sys.exit()
	main()
