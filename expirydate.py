from alice_blue import *
import math
import time
import datetime
from datetime import date,timedelta

def round_nearest(x, num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x, 100)
def nearest_strike_nf(x): return round_nearest(x, 50)


access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
                  access_token=access_token)


ltp_bnf = 33890
bnf_nearest_strike = nearest_strike_bnf(ltp_bnf)


def latest_expiry(bnf_nearest_strike):
    print("Latest Expiry date search activated")
    global date_today

    call = None
    date_today = date.today()
    for i in range(7):
        if call == None:
    # while call == None:
            print("while started")
            try:
                print("try started")
                call = alice.get_instrument_for_fno(symbol="BANKNIFTY", expiry_date=date_today, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
                print("trying different date")
                if call == None:
                    print("No call value added yet")
                    date_today = date_today + timedelta(days=1)
                    print("NEAREST EXPIRY DATE FOUND")
                    print(date_today)
                # else:
                    
                #     return date_today
                #     print(date_today)
            except:
                pass
                # print("date",date_today)
                # return date_today


print("EXPIRY DATE---------->>",latest_expiry(33560))








# def latest_expiry(bnf_nearest_strike):
#     print("Latest Expiry date search activated")
#     global date_today

#     call = None
#     date_today = date.today()
#     while call == None:
#         print("while started")
        
#         call = alice.get_instrument_for_fno(symbol="BANKNIFTY", expiry_date=date_today, is_fut=False, strike=bnf_nearest_strike, is_CE=True)
#         print("trying different date")
#         if call == None:
#             print("No call value added yet")
#             date_today = date_today + timedelta(days=1)
#         else:
#             print("NEAREST EXPIRY DATE FOUND")
#             return date_today
#             print(date_today)

            # print("date",date_today)
            # return date_today



# order_placed = False
# while datetime.now().time() <= time(9,30):
#     time.sleep(30)
# try:
#     while order_placed == False:

