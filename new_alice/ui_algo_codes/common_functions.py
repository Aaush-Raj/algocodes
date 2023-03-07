#make a expiry fnc
#make monthly expiry fnc as well
# get any latest LTP in expiry fnc itself
#orderstatus fnc
#avgprc fnc
# modify fnc
import datetime as dt
from pya3 import *
import math

username = '285915'
api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'

# alice = Aliceblue(user_id=username,api_key=api_key)
# print(alice.get_session_id())

# ltp = 42600
# datecalc = "2022-11-17"
# call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=ltp, is_CE=True)
# print(call)
# print("0000000000000000000000000000000000000000000000000")


def round_nearest(x, num=50): return int(math.ceil(float(x)/num)*num)
def round_100(x): return round_nearest(x, 100)
def round_50(x): return round_nearest(x, 50)


def latest_expiry(alice):
    ins = alice.get_scrip_info(alice.get_instrument_by_symbol('INDICES', "NIFTY BANK"))
    ltp = round_100(dict(ins)['LTP'])
    print(ltp)

    call = False
    datecalc = dt.date.today().strftime("%Y-%m-%d") 
    print(datecalc)
    while call == False:
        try:
            sleep(2)
            call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=ltp, is_CE=True)
            print(call)
            print(datecalc)
            # print(type(datecalc))
            if call['emsg'] =='No Data':
                datecalc = (dt.datetime.strptime(datecalc, "%Y-%m-%d")+  dt.timedelta(days=1)).strftime("%Y-%m-%d")
                call = False
            else:
                call = True
        except:
            pass

    return datecalc


def latest_monthly_expiry(alice):
    call = False
    datecalc = dt.date.today().strftime("%Y-%m-%d") 
    while call == False:
        try:
            sleep(2)
            call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=True, expiry_date=datecalc, strike=None, is_CE=True)
            print(call)
            if call['emsg'] =='No Data':
                datecalc = (dt.datetime.strptime(datecalc, "%Y-%m-%d")+  dt.timedelta(days=1)).strftime("%Y-%m-%d")
                call = False
            else:
                call = True
        except:
            pass

    return datecalc

# print(latest_monthly_expiry())


def order_status_function(alice,oid):
	order_status= None
	for i in range(3):
		print("for")
		try:
			print("try")
			order_details = alice.get_order_history(oid)
			order_status = order_details['Status']
			print(order_status)
			return order_status
		except Exception as e:
			print({e})
			sleep(25)
			pass


def order_modify_put(alice,oid,inst):
	order_details = alice.get_order_history(oid)
	order_status = order_details['Status']
	print("put slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_put = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")

def order_modify_call(alice,oid,inst):
	order_details = alice.get_order_history(oid)
	order_status = order_details['Status']
	print("call slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_call = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")


def modify_ce_order_to_cost(alice,inst,pe_sl_oid, call_sell_avg_price,quantity):
    order_details = alice.get_order_history(pe_sl_oid)
    order_status = order_details['Status']
    print("call slm order status",order_status)
    # if order_status == 'complete':
    if order_status == 'complete':
        ce_sl_cost_price = 0.05 * round((float(call_sell_avg_price))/0.05)
        modify_ce_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.StopLossLimit,quantity=quantity,price = ce_sl_cost_price + 10,trigger_price = ce_sl_cost_price)
        print(modify_ce_to_cost)
    else:
        return("call slm order status is",order_status)

def modify_pe_order_to_cost(alice,inst,ce_sl_oid,put_sell_avg_price,quantity):
    order_details = alice.get_order_history(ce_sl_oid)
    order_status = order_details['Status']
    print("Put slm order status",order_status)
    if order_status == 'complete':    
        pe_sl_cost_price = 0.05 * round((float(put_sell_avg_price))/0.05)
        modify_pe_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(number), order_type=OrderType.StopLossLimit,quantity=quantity,price = pe_sl_cost_price + 10,trigger_price = pe_sl_cost_price)
        print(modify_pe_to_cost)
    else:
        return("Put slm order status is",order_status)


