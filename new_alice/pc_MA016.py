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
# import us_MA016

print("Time stamp: ",dt.datetime.now())

#Alice API

# client_code = us_MA016.client_code
# full_name = us_MA016.full_name
# username = us_MA016.username
# password = us_MA016.password
# api_key = us_MA016.api_key
# twoFA = us_MA016.twoFA
# user_gmail_id = us_MA016.user_gmail_id
# my_gmail_id = 'hiraninitin96@gmail.com'

alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())

def exit_positions():
	tradebook_netwise = alice.get_netwise_positions()
	print(tradebook_netwise)
	position_count = len(tradebook_netwise)
	print("Position count is: ",position_count)

	x = 0

	while x in range(position_count):
    		
		print(tradebook_netwise[x]["Pcode"])
		if tradebook_netwise[x]["Pcode"] == 'MIS':
			token = int(tradebook_netwise[x]["Token"])
			symbol = alice.get_instrument_by_token('NFO',token)
			print(symbol)
			quantity_left = int(tradebook_netwise[x]['Netqty'])
			print(quantity_left)

			if quantity_left != 0:
				if quantity_left < 0:
					print("sell position left")
					quantity_left = alice.place_order(transaction_type=TransactionType.Buy,instrument=symbol,quantity=quantity_left * -1,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
					print("position",x +1,"is sqaured off")
				else:
					print("position",x +1,"is already closed ")
			x = x + 1

def all_cancel_orders():
	total_orders = alice.get_order_history('')
#	print(total_orders)
	pending_orders = []
	for t in total_orders:
		if t['Status'] == 'trigger pending'or t['Status'] == 'open':
			pending_orders.append(t['Nstordno'])

	x = 0

	while x in range(len(pending_orders)):
		oms_id = pending_orders[x]
		print("oms id ",oms_id)
		token = int(alice.get_order_history(oms_id)['token'])
		print(token)
		alice.cancel_order(oms_id)
		x = x + 1

try:

	while dt.datetime.now().time()<= dt.time(14,49,59):
		sleep(1)

	exit_positions()
	all_cancel_orders()
except:
		print(f"some error occured at intial main:::>{e}")
		error = f"{e}"
		exception_type, exception_object, exception_traceback = sys.exc_info()
		line_number = exception_traceback.tb_lineno
		print("An error ocurred at Line number: ", line_number)
		
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.starttls()
		server.login(my_gmail_id,'ielyexucuxmibqem')
		subject = "Error in cliend id:",client_code,"user id:",username
		body = """Error below:\nError =""",error,"""\nLine number:""",line_number

		msg = f'Subject: {subject}\n\n{body}'

		server.sendmail(my_gmail_id,my_gmail_id,msg)
		print('mail sent')
		exit()