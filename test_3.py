from alice_blue import *
import requests, json
import dateutil.parser
import sys
import math
import time
import pandas as pd
import datetime as dt
# import datetime
# from datetime import date,timedelta
from datetime import datetime, timedelta



def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)


access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
                  access_token=access_token)


#------------------------------------------LOGIC FOR GETTING HIGH AND LOW DATA--------------------------------------------------





def get_historical(instrument, from_datetime, to_datetime, interval, indices=False):
    params = {"token": instrument.token,
              "exchange": instrument.exchange if not indices else "NSE_INDICES",
              "starttime": str(int(from_datetime.timestamp())),
              "endtime": str(int(to_datetime.timestamp())),
              "candletype": 3 if interval.upper() == "DAY" else (2 if interval.upper().split("_")[1] == "HR" else 1),
              "data_duration": None if interval.upper() == "DAY" else interval.split("_")[0]}
    lst = requests.get(
        f" https://ant.aliceblueonline.com/api/v1/charts/tdv?", params=params).json()["data"]["candles"]
    records = []
    for i in lst:
        record = {"date": dateutil.parser.parse(i[0]), "open": i[1], "high": i[2], "low": i[3], "close": i[4], "volume": i[5]}
        records.append(record)
    return records


instrument = alice.get_instrument_by_symbol("NSE", "Nifty Bank")
# from_datetime = datetime.now() - timedelta(hours=10)
from_datetime = dt.time(10) - timedelta(minutes=45)
to_datetime = dt.time(10)
interval = "1_MIN"   # ["DAY", "1_HR", "3_HR", "1_MIN", "5_MIN", "15_MIN", "60_MIN"]
indices = True
pd.set_option("max_columns", None) 
pd.set_option("max_rows", None)
df = pd.DataFrame(get_historical(instrument, from_datetime, to_datetime, interval, indices))
high_list = []
df_high = df.iloc[:,2]
df_low = df.iloc[:,3]
for h in df_high:
    high_list.append(h)
# print("THIS IS THE LIST OF ALL THE HIGHEST VALUE OF TODAY's TIMEFRAME",high_list)
highest_number = high_list[0]
for high in high_list:
    if high > highest_number:
        highest_number = high
        
print ("The highest of Banknifty since 9:15 AM is -->",strGreen(highest_number))

