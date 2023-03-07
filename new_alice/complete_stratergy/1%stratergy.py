# import datetime as dt
# print(dt.date.today())
from pya3 import *

import datetime as dt
from datetime import datetime,date, timedelta
import time
alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')


# now = datetime.now() # current date and time

# year = now.strftime("%Y")
# print("year:", year)sl

# month = now.strftime("%m")
# print("month:", month)

# day = now.strftime("%d")
# print("day:", day)

# time = now.strftime("%H:%M:%S")
# print("time:", time)

date_time = dt.date.today().strftime("%d-%m-%Y") 
print("date and time:",date_time)	





def latest_expiry():
    called = None
    call = None
    exp_d = 0
    test = False
    date_today = date.today().strftime("%d-%m-%Y") 
    while called ==None:
        print("WHILE")
        call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=date_today, strike=39600, is_CE=True)
        print(call)
        # if call[1] != 82695:
        if test == False and call['emsg'] =='No Data':
            print("YES CALL IS NONE")
            # date_today = date_today + timedelta(days=1)
            date_today = (datetime.strptime(date_today, "%d-%m-%Y")+  dt.timedelta(days=1)).strftime("%d-%m-%Y")
            print("working")
            print(date_today)
            x = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=date_today, strike=39600, is_CE=True)
            for i in x:
                print(i)
                if i == 25:
                    print("WORKED")
                    test = True
            # if x['emsg'] =='No Data' is False:
            #     break
        else:
            called = True
            print("CALL IS NOT NONE")
            exp_d = date_today
            return exp_d
            break

datecalc =latest_expiry()
print("date--->",datecalc)

# call =None
# call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date="22-08-2022", strike=39600, is_CE=True)
# print(call)

# if call['emsg'] =='No Data':
#     print("TRUE")
# else:
#     print("CALL FALSE")