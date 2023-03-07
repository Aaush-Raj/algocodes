from nsepython import *
from alice_blue import *
import calendar
import datetime as dt
import time as time
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import smtplib
from datetime import date, datetime
from pya3 import *

client_code = 'MA011'
full_name = 'Rahul Jain'
username = '402855'
password = 'rbadera2905'
api_key = "3xlK6fU8vBGuGGkiM6i2JR8L6Odk0DkXOQvQWNiGiYHmJe7UnT8GGFHoL2mTF31nFcKs90Ido8mtVbuQLzDmIMjr1KLtjEtvV5T2TtvlqFXipm8NMI65FikiEdF10Ihc"
#twoFA = '2001'
#client_id = 'JOYtpzRTsp'
#client_secret = 'EhFmofz64EXyWdEklfo5UypeaKE8xdV3B5V7dHeKZxgWVjVWcB2dbNnQPRRsnCUO'
#redirect_url = 'https://ant.aliceblueonline.com/plugin/callback'
user_gmail_id = 'RAHUL.BADERA2001@GMAIL.COM'
my_gmail_id = 'hiraninitin96@gmail.com'

alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())

print(dt.date.today())

net_margin = alice.get_balance()[0]["net"]
print(net_margin)
if net_margin.isdigit():
	print(int(net_margin))

ce = 40000

# current_date  = dt.date.today().strftime("%Y-%m-%d") 
# datecalc = ((dt.datetime.strptime(current_date,"%Y-%m-%d"))  + (dt.timedelta(days=5))).strftime("%Y-%m-%d")
# print(datecalc)

datecalc = str(dt.date.today() + dt.timedelta(days = 5))
print(datecalc)

instrument = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=ce, is_CE=True)
print(instrument)
print(instrument[5])

sell_order = alice.place_order(transaction_type=TransactionType.Sell,instrument=instrument,quantity=25,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
print(sell_order)

print(sell_order["NOrdNo"])