from _thread import start_new_thread
from time import sleep
from threading import Thread
import pymongo
from pymongo import MongoClient
import ssl
from pya3 import *

def scheduled_task():
    client = pymongo.MongoClient("mongodb+srv://aaush:AaushMongoTestAccount@gopassive.niccs6s.mongodb.net/?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_NONE)
    db = client['AlgoTrade']
    scheduler_col =db['scheduled_data']
    algo_data_col =db['test_statergies']
    all_scheduled_data = list(scheduler_col.find({}))
    
    
    for scheduled_data in all_scheduled_data:
        print("ONE")
        username = scheduled_data['username']
        api_key = scheduled_data['api_key']
        scheduled_algo = scheduled_data['scheduled_algo']
        status = scheduled_data['status']
        algo_data = algo_data_col.find_one({'_id':scheduled_algo })
        
#         start_new_thread(main,(username,api_key,algo_data))
        start_new_thread(place_ord,(username,api_key,algo_data))
        print("STARTED THE ALGO FOR",username,"ALGO->"+scheduled_algo)
        
        


order_id_list = []
order_list = []
sl_order_list = []
def main(username,api_key,input_data):
    print(input_data)
    global alice
    
    alice = Aliceblue(user_id=username,api_key=api_key)
    print(alice.get_session_id())
    
    
    algoName = input_data['algoname']
    instrument = input_data['instrument']
    segment = input_data['segment']
    options = input_data['options']
    transcation_type = input_data['transcation_type']
    strike = input_data['strike']
    lots = input_data['lots']
    target = input_data['target']
    stoploss = input_data['stoploss']
#     is_ce= input_data['is_ce']
    
    #below are singular list data
    startTime = input_data['startTime']
    endTime = input_data['endTime']
    move_sl_to_cost = input_data['move_sl_to_cost']
    square_off = input_data['square_off']
    print("ALGONAME "+algoName)
    
#     while datetime.datetime.now().time() < datetime.time(startTime[0],startTime[1])
    for i in range(len(instrument)):
#         thread = Thread(target = place_orders, args = (transcation_type[i],instrument[i].upper(),lots[i],options[i],strike[i],stoploss[i],target[i]))
#         thread.start()

        start_new_thread(place_orders,(transcation_type[i],instrument[i].upper(),lots[i],options[i],strike[i],stoploss[i],target[i]))
        print(transcation_type[i],instrument[i].upper(),lots[i],options[i],strike[i],stoploss[i],target[i])
        
    
    
def place_orders(transaction_type,inst,lots,option,strike,stoploss,target):
    
    if strike == 'ATM':
        info = alice.get_instrument_by_token('INDICES', 26000)
    
    exp = '2023-1-12' 
    
    print(option)
    
    if option == 'CE':
        is_ce = True
    else:
        is_ce = False
        
    
    if inst.upper() =='NIFTY':
        qty = 50*int(lots)
        print(alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26000)))
        strike = int(round(float(alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26000))['LTP'])/50)*50)
        print(strike)

    else:
        qty = 25*int(lots)
        strike = int(round(float(alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26009))['LTP'])/100)*100)
        print(strike)

    
    if transaction_type == 'BUY':
        ttype = TransactionType.Buy
        sl_ttype = TransactionType.Sell
    else:
        ttype = TransactionType.Sell
        sl_ttype = TransactionType.Buy
        

    instrument =alice.get_instrument_for_fno(exch = 'NFO',symbol=inst,expiry_date=exp,is_fut=False,strike=strike,is_CE=is_ce)
    print("INSTRUMENT-->",instrument)
    order = alice.place_order(transaction_type = ttype,
                     instrument = instrument,
                     quantity = qty,
                     order_type = OrderType.Market,
                     product_type = ProductType.Intraday,
                     price = 0.0,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
    print(order)
#     sleep(1)
    oid = order['NOrdNo']
    order_id_list.append(oid)
    
    print(stoploss,"Points on Avg_prc Was given as stoploss")
    print(target,"Points on Avg_prc Was given as Target")
    
    
    
def place_ord(username,api_key,input_data):

        
    algoName = input_data['algoname']
    instrument = input_data['instrument']
    segment = input_data['segment']
    options = input_data['options']
    transcation_type = input_data['transcation_type']
    strike = input_data['strike']
    lots = input_data['lots']
    target = input_data['target']
    stoploss = input_data['stoploss']
#     is_ce= input_data['is_ce']
    
    #below are singular list data
    startTime = input_data['startTime']
    endTime = input_data['endTime']
    move_sl_to_cost = input_data['move_sl_to_cost']
    square_off = input_data['square_off']
    print("ALGONAME "+algoName)
    
    print(lots)
    print(len(instrument))
    for i in range(len(instrument)):
        print("YAHA")
        lots = lots[i]
        print("TOO")
        exp = "2023-01-12"
        is_ce = False
        print("here")
        if instrument[i].upper() =='NIFTY':
            qty = 50*int(lots)
            print(alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26000)))
            strike = int(round(float(alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26000))['LTP'])/50)*50)
            print(strike)

        else:
            qty = 25*int(lots)
            strike = int(round(float(alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26009))['LTP'])/100)*100)
            print(strike)
            
        if transcation_type[i] =="BUY":
            ttype = TransactionType.Buy
            sl_ttype = TransactionType.Sell
        else:
            ttype = TransactionType.Sell
            sl_ttype = TransactionType.Buy
            
        instrument_t =alice.get_instrument_for_fno(exch = 'NFO',symbol=instrument[i].upper(),expiry_date=exp,is_fut=False,strike=strike,is_CE=is_ce)
        print(instrument_t)
        order = alice.place_order(transaction_type = ttype,
                         instrument = instrument_t,
                         quantity = qty,
                         order_type = OrderType.Market,
                         product_type = ProductType.Intraday,
                         price = 0.0,
                         trigger_price = None,
                         stop_loss = None,
                         square_off = None,
                         trailing_sl = None,
                         is_amo = False)
        print("ORDER PLACED", order)
    
    
def place_sl_orders():
#     get_avg_prc(oid)
    pass
def get_avg_prc(oid):
    order_details = alice.get_order_history(oid)
    avg_price = order_details['Avgprc']
    return avg_price

def get_ord_status(oid):
    order_details = alice.get_order_history(oid)
    ord_status = order_details['Status']
    return ord_status

# main(input_data)

scheduled_task()