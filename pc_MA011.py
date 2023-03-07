import datetime as dt
import time
from pya3 import *


api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"       
user_id = "285915" 

alice = Aliceblue(user_id=user_id,api_key=api_key)
print(alice.get_session_id())


def exit_positions():
	tradebook_netwise = alice.get_netwise_positions()
	position_count = len(tradebook_netwise)
	print("Position count is: ",position_count)

	x = 0

	while x in range(position_count):
		print(type(x))
		if tradebook_netwise[x]["Pcode"] == 'MIS':
			token = int(tradebook_netwise[x]['Token'])
			symbol = alice.get_instrument_by_token('NFO',token)
			quantity_left = int(tradebook_netwise[1][Netqty])

			if quantity_left != 0:
				if quantity_left < 0:
					quantity_left = alice.place_order(transaction_type=TransactionType.Buy,instrument=symbol,quantity=quantity_left* -1,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
					print("position",x +1,"is sqaured off")
				else:
					print("position",x +1,"is already closed ")
			x = x + 1

def all_cancel_orders():
	total_orders = alice.get_order_history('')
	pending_orders = []
	for t in total_orders:
		if t['Status'] == 'pending' or t['Status'] == 'open':
			pending_orders.append(t['Nstordno'])
	x = 0

	while x in range(len(pending_orders)):
		oms_id = pending_orders[x]
		token = int(alice.get_order_history(str(oms_id))['token'])
		alice.cancel_order(alice.get_instrument_by_token('NFO', token), oms_id)
		x = x + 1

while dt.datetime.now().time()<= dt.time(14,50):
	time.sleep(1)

exit_positions()
all_cancel_orders()
