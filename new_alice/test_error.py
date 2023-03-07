from pya3 import *

def get_ce_curr_price(ce):
	print('get_ce_curr_price')
	global bnf_call

	bnf_call = alice.get_instrument_for_fno(exch = 'NFO',symbol='BANKNIFTY',expiry_date=datecalc,is_fut=False,strike=ce,is_CE=True)
	sell_ce_option(bnf_call)


def get_pe_curr_price(pe):
	print('get_pe_curr_price')
	global bnf_put

	bnf_put = alice.get_instrument_for_fno(exch = 'NFO',symbol='BANKNIFTY',expiry_date=datecalc,is_fut=False,strike=pe,is_CE=False)
	sell_pe_option(bnf_put)

def sell_ce_option(bnf_call):
	global quantity,sell_order_call
	quantity=no_of_lots*int(bnf_call[5])
	sell_order_call = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
