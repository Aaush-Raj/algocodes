from alice_blue import *
import calendar
import datetime as dt
from time import sleep
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import smtplib
from pya3 import *
#Alice API

full_name = 'Rahul Jain'
username = '523413'
password = '29rahul2001'
twoFA = '2001'
client_id = 'JOYtpzRTsp'
api_key = "bUDQz1uu3XUxlfcj5J6CWU2Cs0HTqqlm38TQpt7Fr3iSKRE5WDv8vklNq9qkr6Gv3DKoRZsYkZOeNixCmyPXeX0kSh946FQWqKbAHMGh6BVgPoHilcrhEScJYPGQ3xkL"
client_secret = 'EhFmofz64EXyWdEklfo5UypeaKE8xdV3B5V7dHeKZxgWVjVWcB2dbNnQPRRsnCUO'
redirect_url = 'https://ant.aliceblueonline.com/plugin/callback'
user_gmail_id = 'RAHUL.BADERA2001@GMAIL.COM'
my_gmail_id = 'hiraninitin96@gmail.com'

alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())

#print(alice.get_balance()) # get balance / margin limits
#print(alice.get_profile()) # get profile
#print(alice.get_daywise_positions()) # get daywise positions
# print(alice.get_netwise_positions()) # get netwise positions
#print(alice.get_holding_positions()) # get holding positions

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
			print(token)
			symbol = alice.get_instrument_by_token('NFO',token)
			quantity_left = int(tradebook_netwise[x]['Netqty'])
			print(quantity_left)

			if quantity_left != 0:
				if quantity_left < 0:
					print("sell position left")
					quantity_left = alice.place_order(transaction_type=TransactionType.Buy,instrument=symbol,quantity=int(quantity_left) * -1,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
					print("position",x +1,"is sqaured off")
				else:
					print("position",x +1,"is already closed ")
			x = x + 1

def all_cancel_orders():
	total_orders = alice.get_order_history('')
	print(total_orders)
	pending_orders_count = len(total_orders)
	print(pending_orders_count)

	x = 0

	while x in range(pending_orders_count):
		oms_id = total_orders[x]['Nstordno']
		tokenid = total_orders[x]['token']
		print(alice.cancel_order(alice.get_instrument_by_token('NFO', int(tokenid)),oms_id)) #Cancel an open order
		# alice.cancel_order(oms_id)
		x = x + 1

while dt.datetime.now().time()<= dt.time(14,50):
	sleep(1)

exit_positions()
# all_cancel_orders()
