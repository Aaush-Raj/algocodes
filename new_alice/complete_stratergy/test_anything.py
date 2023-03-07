# import warnings
# warnings.filterwarnings('ignore')
# import math
# from smartapi import SmartConnect
# import time
# import requests
# import pandas as pd
# # import datetime as dt
# import datetime
# from datetime import date,timedelta



# def round_nearest(x, num=50): return int(round((x/100))*100)
# def nearest_strike_bnf(x): return round_nearest(x, 100)

# apikey = 'GHs4KzGv'
# username = 'A718575'
# pwd = '@ankitraj1'



# obj =SmartConnect(api_key=apikey)
# data = obj.generateSession(username,pwd)


# url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
# d = requests.get(url).json()
# token_df = pd.DataFrame.from_dict(d)
# print(token_df['expiry'] )
# x=pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
# print(x)
# token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
# token_df = token_df.astype({'strike': float})
# #token_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']==date(2021,6,10)) ]
# print(token_df)


from pya3 import *
alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')

print(alice.get_session_id())

import datetime as dt
import time
def get_date_curr_expriry(ce):
    print('date_curr_expiry')
    global datecalc
    print('ATM CE is: ',ce)
    call = None
    datecalc = dt.date.today()
    # get current week expiry date
    while call == None:
        try:
            call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=ce, is_CE=True)
            if call == None:
                print('No value in call')

                datecalc = datecalc	+ dt.timedelta(days = 1)

        except:
            pass
    print(datecalc)
    return datecalc
    
get_date_curr_expriry(39000)