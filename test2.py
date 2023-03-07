from alice_blue import *
import math
import time
import datetime
from datetime import date,timedelta


def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)



access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
                  access_token=access_token)

symbol = 'Nifty Bank'
bnf_script = alice.get_instrument_by_symbol('NSE', symbol)

time.sleep(2)
socket_opened = False


def event_handler_quote_update(message):
    # print(f"quote update {message}")
    global ltp_bnf
    ltp_bnf = message['ltp']
    print("BANKNIFTY LTP -------------->>>>>>>", ltp_bnf)
    # print('LTP OF BANKNIFTY IS:',ltp_bnf)


def open_callback():
    global socket_opened
    socket_opened = True


alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)
while(socket_opened == False):
    pass

alice.subscribe(bnf_script, LiveFeedType.COMPACT)
time.sleep(10)

def open_socket_now():
    global socket_opened
    socket_opened = False
    alice.start_websocket(subscribe_callback=event_handler_quote_update,
                          socket_open_callback=open_callback, run_in_background=True)
    time.sleep(2)

    while (socket_opened == False):
        pass


if socket_opened == False:
    open_socket_now()

bnf_nearest_strike = nearest_strike_bnf(ltp_bnf)
# print("THE CURRENT PRICE OF BANK NIFTY IS ----------->>", ltp_bnf)
# print("THE NEAREST STRIKE PRICE OF BANK NIFTY IS ---------->>", bnf_nearest_strike)
alice.unsubscribe(bnf_script, LiveFeedType.COMPACT)


def latest_expiry():
    call = None
    exp_d = 0
    date_today = date.today()
    while call ==None:
        call = alice.get_instrument_for_fno(symbol="BANKNIFTY", expiry_date=date_today, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
        if call ==None:
            date_today = date_today + timedelta(days=1)
        elif call != None:
            exp_d = date_today
            return exp_d
            break

expiry_date =latest_expiry()
print("EXPIORY DATE IS",expiry_date)

bn_call = alice.get_instrument_for_fno(symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
alice.subscribe(bn_call, LiveFeedType.MARKET_DATA)
time.sleep(10)

nearest_strike_ltp = float(int(ltp_bnf))
x = ltp_bnf
stoploss_amt = x*0.25
stoploss = float(int(ltp_bnf - stoploss_amt))
trigger_price = float(int(stoploss + 10))

print("LATEST STRIKE PRICE IS",bnf_nearest_strike)
print("EXPIORY DATE IS",expiry_date)
print("LATEST STRIKE's LTP IS",nearest_strike_ltp)
print("STOPLOSS IS",stoploss)
print("TRIGERED PRICE IS",trigger_price)


# def get_current_price(bnf_nearest_strike):

#     bankifty_call = alice.get_instrument_for_fno(symbol = "BANKNIFTY", expiry_date=date_today, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
#     alice.subscribe(banknifty_call, LiveFeedType.MARKET_DATA)
#     time.sleep(2)
#     print("LTP -------->>>>>>>>>>>>>",ltp)
#     ce_price = ltp




# print(
#    alice.place_order(transaction_type = TransactionType.Buy,
#                      instrument = alice.get_instrument_for_fno(symbol='BANKNIFTY', expiry_date=datetime.date(2022, 6, 16), is_fut=False, strike=bnf_nearest_strike, is_CE=True),
#                      quantity = 1,
#                      order_type = OrderType.StopLossLimit,
#                      product_type = ProductType.Intraday,
#                      trigger_price =trigger_price,
#                      stop_loss = stoploss,
#                      is_amo = False)
# )
# PLACING ORDER CODE
# print(alice.place_order(TransactionType.Buy, bn_call,
    #   1, OrderType.Market, ProductType.Intraday))