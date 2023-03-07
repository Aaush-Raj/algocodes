import sys
from pya3 import *
from datetime import datetime
import datetime as dt
from time import sleep
import smtplib
from nsepython import expiry_list
from common_functions import generate_session, check_margin, order_status, get_oid, ap_generator, latest_expiry
from send_message import send_email, send_msg

ltp_bnf = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []

def socket_open():  # Socket open callback function
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
        alice.subscribe(subscribe_list)

def socket_close():  # On Socket close this callback function will trigger
    global socket_opened, ltp_bnf
    socket_opened = False
    ltp_bnf = 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global ltp_bnf
    ltp_bnf = 0
    print("Error :", message)

def feed_data(message):  # Socket feed data will receive in this callback function
    global ltp_bnf, subscribe_flag
    feed_message = json.loads(message)
#     ltp_bnf = feed_message['lp'] if 'lp' in feed_message else ltp_bnf
#     print(ltp_bnf)
    
    if feed_message["t"] == "ck":
#         print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
        subscribe_flag = True
#         print("subscribe_flag :", subscribe_flag)
        pass
    elif feed_message["t"] == "tk":
#         print("Token Acknowledgement status :%s " % feed_message)
#         print("-------------------------------------------------------------------------------")
        pass
    else:
#         print("Feed :", feed_message)
        ltp_bnf = feed_message[
            'lp'] if 'lp' in feed_message else ltp_bnf  # If ltp_bnf in the response it will store in ltp_bnf variable
        print(ltp_bnf)
# Socket Connection Request

    
def main():
    global alice,socket_opened,username,ltp_bnf,bnf_call,order_placed,quantity,bnf_put
    try:
        alice = Aliceblue(user_id=username,api_key=api_key)

        #generating Session
        generate_session(alice,username)
        #Checking Margin 
        # check_margin(alice,client_code,username,no_of_lots,required_margin,user_gmail_id)

        #starting alice websocket 
        alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)
        while not socket_opened:
            print("Socket not opened")
            pass

        #subscribing websocket
        subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
        alice.subscribe(subscribe_list)
        print("SUBSCRIBED ",symbol)

        sleep(2)

        order_placed = False
        modify_order = False

        while dt.datetime.now().time() <= dt.time(start_hr,start_min,start_sec):
            sleep(0.5)

        while order_placed == False:

            #fetching latest strike and ltp
            curr_ltp=int(float(ltp_bnf))
            ce_stk_ltp = curr_ltp + (stk_ce*strike_range)
            pe_stk_ltp = curr_ltp + (stk_pe*strike_range)
            print("CE STRIKE = ",ce_stk_ltp)
            print("PE STRIKE = ",pe_stk_ltp)
            print(curr_ltp)
            ce,pe = int(round(ce_stk_ltp/strike_range)*strike_range), int(round(pe_stk_ltp/strike_range)*strike_range)
            ce,pe = 43300,43300
            print('ATM CE ',ce,' ATM PE ',pe)
            
            #unsubscribing websocket as we don't need the live ltp anymore.
            unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
            alice.unsubscribe(unsubscribe_list)
            print("UNSUBSCRIBED ",symbol)

            #placing our Initial orders,  both CALL and PUT will be sold in this single function : place_orders()
            place_orders(ce,pe)
            sleep(2)

            #placing CALL side stoloss order
            place_ce_sl_order()

            #placing PUT side stoloss order
            place_pe_sl_order()
            
            order_placed = True

    except Exception as e:
        print(f"some error occured at intial main:::>{e}")
        error = f"{e}"
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("An error ocurred at Line number: ", line_number)
        sys.exit()



def place_orders(ce,pe):
    global ce_sell_oid, pe_sell_oid, bnf_call, bnf_put

    bnf_call = alice.get_instrument_for_fno(exch = 'NFO',symbol=trading_symbol,expiry_date=current_expiry_date,is_fut=False,strike=ce,is_CE=True)
    print(bnf_call)
    bnf_put = alice.get_instrument_for_fno(exch = 'NFO',symbol=trading_symbol,expiry_date=current_expiry_date,is_fut=False,strike=pe,is_CE=False)
    print(bnf_call,bnf_put)
    ce_sell = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
    pe_sell = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

    print(ce_sell)
    print(pe_sell)

    if ce_sell['stat'] =="Ok":
        print("CE ORDER PLACED SUCESSFULY!")
    else:
        for i in range(1):
            print(ce_sell)
            print("RETRYING TO PLACE ORDER!")
            ce_sell = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
        
            if pe_sell['stat'] =="Ok":
                break
            else:
                print("TRYING AGAIN")

        if ce_sell['stat'] !="Ok":
            print("TRIED 3 Times to place CE Order but still it's not placed. So sending you a message!")
            msg = ("CALL ORDER IS NOT PLACED FOR USER",username)
            send_msg(msg)
    
    try:
        ce_sell_oid = get_oid(ce_sell)
    except Exception as e:
        print({e})

    
    if pe_sell['stat'] =="Ok":
        print("PE ORDER PLACED SUCESSFULY!")
    else:
        for i in range(1):
            print(pe_sell)
            print("RETRYING TO PLACE ORDER!")
            pe_sell = alice.place_order(transaction_type=TransactionType.Sell,instrument=bnf_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
            if pe_sell['stat'] =="Ok":
                break
            else:
                print("TRYING AGAIN")
        if pe_sell['stat'] !="Ok":
            print("TRIED 3 Times to place PE Order but still it's not placed. So sending you a message!")
            msg = ("PUT ORDER IS NOT PLACED FOR USER",username)
            send_msg(msg)
  
    try:
        pe_sell_oid = get_oid(pe_sell)
    except Exception as e:
        print({e})
    
def place_ce_sl_order():
    if order_status(alice,ce_sell_oid) =='complete':
        ce_sell_avg_p = ap_generator(ce_sell_oid)
        if sl_type =='PERCENT':
            slm_call_buy_price = 0.05 * round((float(ce_sell_avg_p) * sl_ce_value)/0.05)
        else:
            slm_call_buy_price = 0.05 * round((float(ce_sell_avg_p) + sl_ce_value)/0.05)

        slm_limit_call_buy_price = float(round(slm_call_buy_price) + 10)
        sl_call_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

        global oid_call_slm

        if sl_call_order['stat'] != 'Ok':
            for i in range(1):
                sl_call_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                if sl_call_order["stat"] == 'Ok':
                    break
                else:
                    print("RETRYING TO PLACE SLM CALL ORDER ONCE AGAIN")

            if sl_call_order['stat'] !='Ok':
                msg = ('SL CALL ORDER NOT PLACED FOR USER ',username)
                send_msg(msg)
        else:
            print("CALL SLM PLACED")

        try:
            oid_call_slm = get_oid(sl_call_order)
            call_slm_order_status = order_status(alice,oid_call_slm)
            print("Call SLM order placed with status:",call_slm_order_status)
        except Exception as e:
            print({e})

    else:
        msg= 'CE Order not placed yet'
        send_msg(msg)

def place_pe_sl_order():
    if order_status(alice,pe_sell_oid) =='complete':
        pe_sell_avg_p = ap_generator(pe_sell_oid)
        if sl_type =='PERCENT':
            slm_put_buy_price = 0.05 * round((float(pe_sell_avg_p) * sl_pe_value)/0.05)
        else:
            slm_put_buy_price = 0.05 * round((float(pe_sell_avg_p) +  sl_pe_value)/0.05)

        slm_limit_put_buy_price = float(round(slm_put_buy_price) + 10)
        sl_put_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

        global oid_put_slm

        if sl_put_order['stat'] != 'Ok':
            for i in range(3):
                sl_put_order = alice.place_order(transaction_type=TransactionType.Buy,instrument=bnf_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                if sl_put_order["stat"] == 'Ok':
                    break
                else:
                    print("RETRYING TO PLACE SLM PUT ORDER ONCE AGAIN")

            if sl_put_order['stat'] !='Ok':
                msg = ('SL PUT ORDER NOT PLACED FOR USER ',username)
                send_msg(msg)
        else:
            print("PUT SLM PLACED")

        try:
            oid_put_slm = get_oid(sl_put_order)
            put_slm_order_status = order_status(alice,oid_put_slm)
            print("Call SLM order placed with status:",put_slm_order_status)
        except Exception as e:
            print({e})        
    else:
        msg= 'PE Order not placed yet'
        send_msg(msg)

#Getting All the Necessary Variables

# client_code = us_MA016.client_code
# full_name = us_MA016.full_name
# username = us_MA016.username
# password = us_MA016.password
# api_key = us_MA016.api_key
# twoFA = us_MA016.twoFA
# user_gmail_id = us_MA016.user_gmail_id
# my_gmail_id = 'hiraninitin96@gmail.com'
# 
username = '285915'
api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'
client_code = "TEST"
alice  = Aliceblue(username,api_key)
session_id = alice.get_session_id()
print(len(session_id))
print(session_id)
if session_id['apikey'] != None:
    print("IT WORKED")

sys.exit()

order_placed = False
modify_order = False
required_margin = 190000
symbol = 'NIFTY BANK' #NIFTY BANK, NIFTY 50 ,  NIFTY FIN SERVICE
trading_symbol = 'BANKNIFTY' #NIFTY #BANKNIFTY #FINNIFTY

stk_ce = 0 #If ATM then stk = 0 , if OTM1 then change stk to 1(stk=1) if ITM then change the stk to -1 , for ITM use -1,-2,-3,-4,etc and for OTM use 1,2,3,4,etc and for ATM just use 0
stk_pe = 0 #If ATM then stk = 0 , if OTM1 then change stk to 1(stk=1) if ITM then change the stk to -1 , for ITM use -1,-2,-3,-4,etc and for OTM use 1,2,3,4,etc and for ATM just use 0


if trading_symbol =='BANKNIFTY':
    strike_range = 100

elif trading_symbol =='NIFTY':
    strike_range = 50

elif trading_symbol =='FINNIFTY':
    strike_range = 50


start_hr, start_min, start_sec = 9,19,59
print("STARTING TIME IS: ",start_hr,":",start_min,":",start_sec)

exit_hr,exit_min,exit_sec = 15,14,59
print("EXIT TIME IS: ",exit_hr,":",exit_min,":",exit_sec)

current_expiry_date =latest_expiry(trading_symbol)
print(str(current_expiry_date))

no_of_lots = 10
quantity = no_of_lots* 25

sl_type = 'PERCENT' #sl_type can be "PERCENT" or "POINTS"

sl_ce_value = 1.20
sl_pe_value = 1.20

socket_opened= False

# starting main script

if (__name__=='__main__'):
    # send_msg("TESTING")
    print('Started straddle')
    main()
