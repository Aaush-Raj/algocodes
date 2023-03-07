#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 14:47:28 2020

@author: rk_algopy
"""


#import logging
import datetime
import sys
from datetime import date, timedelta,datetime,time
import statistics
from time import sleep
from alice_blue import *
import pandas as pd




# Config
username = 'username'
password = 'passwrd'
api_secret = ''
twoFA = '1'
NIFTY_BANK_IDX = ''
NSE_holiday = [date(2020, 10, 5),date(2020, 11, 16),date(2020, 11, 30),date(2020, 12, 25)]
alice = None
socket_opened = False
NIFTY_BANK_IDX= ''
no_of_lots=1
sl_percentage=.5



def event_handler_quote_update(message):
    global ltp
    #print(message)
    ltp = message['ltp']
    print('LTP OF SELECTED SCRIPT',ltp)

def open_callback():
    global socket_opened
    socket_opened = True
    
def open_socket_now():
    global socket_opened

    socket_opened = False
    alice.start_websocket(subscribe_callback=event_handler_quote_update,
                          socket_open_callback=open_callback,
                          run_in_background=True)
    sleep(10)
    while(socket_opened==False):    # wait till socket open & then subscribe
        pass 

    

 
# MAIN LOGIC HERE  ########################################################################    
    
def main():
    global alice,socket_opened,username,password,twoFA,ltp,api_secret,ltp,bn_call,order_placed,ce_price,pe_price
    
    while alice is None:
        print('logging in alice')
        try:
            access_token =  AliceBlue.login_and_get_access_token(username=username, password=password, twoFA=twoFA,  api_secret=api_secret)
            alice = AliceBlue(username=username, password=password, access_token=access_token, master_contracts_to_download=['NSE','NFO'])
        except:
            print('login failed Alice..retrying in 3 mins')
            sleep(180)
            pass
 
    if socket_opened == False:
        open_socket_now()
    get_bnf_month()
    

    
    alice.subscribe(banknifty_script, LiveFeedType.MARKET_DATA)   
    sleep(10)
     
 
    order_placed = False

    while datetime.now().time()<= time(9,30):
        sleep(60)
    try:
        while order_placed == False:
                    
                    curr_ltp = ltp
                    atm_ce,atm_pe = int(curr_ltp/100)*100,int(curr_ltp/100)*100
                    print('atm_ce',atm_ce,'atm_pe',atm_pe)
                    alice.unsubscribe(banknifty_script, LiveFeedType.MARKET_DATA)
                    get_date_curr_expiry(atm_ce)
                    get_ce_curr_price(atm_ce)
                    get_pe_curr_price(atm_pe)
                    order_placed = True
       
    except Exception as e:
                #rint('some error occured at initial main:::->',e)
                print(f"some error occured at initial main:::->{e}")
                
                        
"""

def get_bnf_month():
    global NIFTY_BANK_IDX,banknifty_script
    
    MON = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    curr_mon = datetime.now().month
    while curr_mon < 13:
        mon = MON[curr_mon-1]   
        NIFTY_BANK_IDX = f"BANKNIFTY {mon} FUT"
         
        banknifty_script = alice.get_instrument_by_symbol('NFO', NIFTY_BANK_IDX)
        if banknifty_script is None:
            curr_mon = curr_mon + 1
        else:
            token_bnf = banknifty_script[1]
            print('final',{banknifty_script})
            break           
"""

def get_bnf_month():
    global NIFTY_BANK_IDX,banknifty_script
    
    MON = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    curr_mon = datetime.now().month
    banknifty_script=None
    while banknifty_script == None:
        mon = MON[curr_mon-1]   
        NIFTY_BANK_IDX = f"BANKNIFTY {mon} FUT"
         
        banknifty_script = alice.get_instrument_by_symbol('NFO', NIFTY_BANK_IDX)
        
        curr_mon = curr_mon + 1
   
        token_bnf = banknifty_script[1]
    print('final bnf',{banknifty_script})
   
                                    
def get_ce_curr_price(atm_ce):
    print('get_ce_curr_price')
    global bn_call,token_ce,ce_order_placed,ce_sl_price 
  
    #print(atm_ce)
    bn_call = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date= datecalc, is_fut=False, strike=atm_ce, is_CE = True)
    alice.subscribe(bn_call, LiveFeedType.COMPACT)
    sleep(1)
    ce_price=ltp
    sell_ce_option(bn_call,ce_price)
        
       
    print(f"sell ce order placed at price :{ltp}")  
    alice.unsubscribe(bn_call, LiveFeedType.COMPACT)  
    
        
def get_pe_curr_price(atm_pe): 
    print('get_pe_curr_price')
    global bn_put,token_pe,pe_order_placed,pe_sl_price
    
    bn_put = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date= datecalc, is_fut=False, strike=atm_pe, is_CE = False)
    alice.subscribe(bn_put, LiveFeedType.COMPACT)
    sleep(1)
    pe_price=ltp
    sell_pe_option(bn_put,pe_price)
    print(f"sell pe order placed at price :{ltp}")  
    alice.unsubscribe(bn_put, LiveFeedType.COMPACT)  
  
          
        
def get_curr_mtm():
    try:
        global todays_max_min_pnl
        my_positions = client.positions()
        MTM,PnL = 0,0
        for pos in my_positions:
            MTM = pos['MTOM'] + MTM
            PnL = pos['BookedPL'] + PnL
        Net_PnL = MTM + PnL
        todays_max_min_pnl.append(Net_PnL)
        return Net_PnL
    except:
        pass

def get_date_curr_expiry(atm_ce):
    print('date_curr_expiry')
    global datecalc
    print('atm_ce',atm_ce)
    call = None
    datecalc = date.today()
    #get current week expiry date
    while call == None:  
        #print(datesrch)
        try:
            call = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date= datecalc, is_fut=False, strike=atm_ce, is_CE = True)
            if call == None:
                print('No values in call')

                datecalc = datecalc + timedelta(days=1)


        except:
            pass


def sell_ce_option(bn_call,ce_price):
    quantity = no_of_lots*int(bn_call[5])
    
    sell_order = alice.place_order(transaction_type = TransactionType.Sell,
                             instrument = bn_call,
                             quantity = quantity,
                             order_type = OrderType.Market,
                             product_type = ProductType.Intraday,
                             price = 0.0,
                             trigger_price = None,
                             stop_loss = None,
                             square_off = None,
                             trailing_sl = None,
                             is_amo = False)
    sleep(1)
    if sell_order['status'] == 'success':
        sl_order = alice.place_order(transaction_type = TransactionType.Buy,
                         instrument = bn_call,
                         quantity = quantity,
                         order_type = OrderType.StopLossLimit,
                         product_type = ProductType.Intraday,
                         price = 0.0,
                         trigger_price = 1.5*ce_price,
                         stop_loss = None,
                         square_off = None,
                         trailing_sl = None,
                         is_amo = False)

def sell_pe_option(bn_put,pe_price):
    quantity = no_of_lots*int(bn_put[5])
    
    sell_order = alice.place_order(transaction_type = TransactionType.Sell,
                             instrument = bn_put,
                             quantity = quantity,
                             order_type = OrderType.Market,
                             product_type = ProductType.Intraday,
                             price = 0.0,
                             trigger_price = None,
                             stop_loss = None,
                             square_off = None,
                             trailing_sl = None,
                             is_amo = False)
    sleep(1)
    if sell_order['status'] == 'success':
        sl_order = alice.place_order(transaction_type = TransactionType.Buy,
                         instrument = bn_put,
                         quantity = quantity,
                         order_type = OrderType.StopLossLimit,
                         product_type = ProductType.Intraday,
                         price = 0.0,
                         trigger_price = 1.5*pe_price,
                         stop_loss = None,
                         square_off = None,
                         trailing_sl = None,
                         is_amo = False)
    
  
           
    
if(__name__ == '__main__'):
    print('started Straddle')
   
    if date.today() in NSE_holiday:
        print('Enjoy!!..Its a no trade day')
        sys.exit()
    main()
        


   
    
