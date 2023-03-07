from alice_blue import *
import sys
import math
import time
import datetime
from datetime import date,timedelta
from entry_trade import sl_ce_oid, bn_ce_trade, sl_pe_order, bn_pe_trade, quantity, strRed
from credentials import alice

print(strRed("YES THIS IS WORKING"))
def order_status(oid):    
    order_details =alice.get_order_history(oid)
    order_status = order_details['data'][0]['order_status']
    return order_status

def exit_orders():
    if order_status(sl_ce_oid) == "trigger pending":
        print("SL of Call order is Still pending , so we it will get cancelled at specefied time.")
        alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_ce_trade, product_type=ProductType.Intraday, order_id=str(sl_ce_oid), order_type=OrderType.Market,quantity=quantity)
    
    else:
        print("SL of Call order has been executed.So we will not place any exit orders now")
        
    if order_status(sl_pe_order) == "trigger pending":
        print("SL of PUT order is Still pending , so we it will get cancelled at specefied time.")
        alice.modify_order(transaction_type=TransactionType.Buy, instrument=bn_pe_trade, product_type=ProductType.Intraday, order_id=str(sl_pe_order), order_type=OrderType.Market,quantity=quantity)
    else:
        print("SL of PUT order has been executed.So we will not place any exit orders now")
    
   
#EXIT ORDER LOGIC
while datetime.datetime.now().time() < datetime.time(15,10):
    print("wait for the time to be 15:10 ; Right now the time is only -->)",datetime.datetime.now().time())
    time.sleep(5)
try:
    exit_orders()
    print("DONE FOR THE DAY, HOPE YOU MADE GOOD PROFIT.")
    
except Exception as e:
    print(strRed(f"ERROR---->>>>{e}"))
