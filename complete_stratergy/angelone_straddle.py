import warnings
warnings.filterwarnings('ignore')
import math
from smartapi import SmartConnect
import time
import requests
import pandas as pd
# import datetime as dt
import datetime
from datetime import date,timedelta



def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)

apikey = 'GHs4KzGv'
username = 'A718575'
pwd = '@ankitraj1'



obj=SmartConnect(api_key=apikey)
data = obj.generateSession(username,pwd)
# data
#refreshToken= data['data']['refreshToken']
#feedToken=obj.getfeedToken()
#userProfile= obj.getProfile(refreshToken)
#userProfile


# In[ ]:


obj.position()


# In[ ]:


obj.ltpData('NFO','BANKNIFTY24JUN21FUT','48506')


# In[ ]:


def place_order(token,symbol,qty,buy_sell,ordertype,price,variety= 'NORMAL',exch_seg='NSE',triggerprice=0):
    try:
        orderparams = {
            "variety": variety,
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "SELL",
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty,
            "triggerprice":triggerprice
            }
        print(orderparams)
        orderId=obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
    except Exception as e:
        print(f"ERROR---->>>>{e}")
        


def place_sl_order(token,symbol,qty,buy_sell,ordertype,price,variety= 'STOPLOSS',exch_seg='NSE',triggerprice=0):
    try:
        orderparams = {
            "variety": variety,
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "BUY",
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty,
            "triggerprice":triggerprice
            }
        print(orderparams)
        orderId=obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
    except Exception as e:
        print(f"ERROR---->>>>{e}")



def place_exit_order(token,symbol,qty,buy_sell,ordertype,price,variety= 'NORMAL',exch_seg='NSE',triggerprice=0):
    try:
        orderparams = {
            "variety": variety,
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "BUY",
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty,
            "triggerprice":triggerprice
            }
        print(orderparams)
        orderId=obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
    except Exception as e:
        print(f"ERROR---->>>>{e}")

# In[ ]:


url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
d = requests.get(url).json()
token_df = pd.DataFrame.from_dict(d)
token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
token_df = token_df.astype({'strike': float})
#token_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']==date(2021,6,10)) ]
print(token_df)


# In[ ]:


def getTokenInfo (symbol, exch_seg ='NSE',instrumenttype='OPTIDX',strike_price = '',pe_ce = 'CE',expiry_day = None):
    df = token_df
    strike_price = strike_price*100
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE') ]
        return eq_df[eq_df['name'] == symbol]
    elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return df[(df['exch_seg'] == 'NFO') & (df['expiry']==expiry_day) &  (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])



expiry_day = date(2022,8,11)

symbol = 'BANKNIFTY'

spot_token = getTokenInfo(symbol).iloc[0]['token']
ltpInfo = obj.ltpData('NSE',symbol,spot_token)
indexLtp = ltpInfo['data']['ltp']


ATMStrike = nearest_strike_bnf(indexLtp)

ce_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'CE',expiry_day).iloc[0]
# ce_strike_symbol
pe_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'PE',expiry_day).iloc[0]
# pe_strike_symbol


while dt.datetime.now().time() < datetime.time(12,19):
    print("wait for the time to be 9:20 ; Right now the time is only -->)",datetime.datetime.now().time())
    time.sleep(5)
try:
    place_order(ce_strike_symbol['token'],ce_strike_symbol['symbol'],ce_strike_symbol['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')
    place_order(pe_strike_symbol['token'],pe_strike_symbol['symbol'],pe_strike_symbol['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')

   
except Exception as e:
    print(f"ERROR---->>>>{e}")
    
    
while dt.datetime.now().time() < datetime.time(15,10):
    time.sleep(2)
    print("Exit order execution time pending")
try:
    place_exit_order(ce_strike_symbol['token'],ce_strike_symbol['symbol'],ce_strike_symbol['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')
    place_exit_order(pe_strike_symbol['token'],pe_strike_symbol['symbol'],pe_strike_symbol['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')

except Exception as e:
    print(f"ERROR---->>>>{e}")