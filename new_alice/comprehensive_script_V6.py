import sys
from pya3 import *
from datetime import datetime
import datetime as dt
from time import sleep
import smtplib
# from nsepython import expiry_list
from common_functionsV2 import generate_session, check_margin, order_status, get_oid, ap_generator, latest_expiry,monthly_expiry, modify_ce_order_to_cost,modify_pe_order_to_cost, get_ltp_info,strLightPurple,strGreen,strRed,strBold, below_closest_value, above_closest_value, closest_value
from send_message import send_email, send_msg
# import us_HUF028
from threading import Thread

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
    global alice,socket_opened,username,ltp_bnf,ins_call,quantity,ins_put, instrument_ce, instrument_pe
    try:
        alice = Aliceblue(user_id=username,api_key=api_key)

        #generating Session
        generate_session(alice,username)
        #Checking Margin 
        # check_margin(alice,client_code,username,no_of_lots,required_margin,user_gmail_id)


        #subscribing websocket
        if get_closest_val == True:
            print("CLOSEST LOGIC IS TRUE!!, SO WE WON'T OPEN WEBSOCKET")
            instrument_ce,instrument_pe = get_inst_ce_pe(trading_symbol,str(expiry_date))
        else:
            print("CLOSEST PREMIUM LOGIC IS NOT USED< SO WE WILL USE WEBSOCKET TO GET LATEST STRIKES    ")
            #starting alice websocket 
            alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)
            while not socket_opened:
                pass

            subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
            alice.subscribe(subscribe_list)
            print("SUBSCRIBED ",strLightPurple(symbol))

            sleep(2)

        while dt.datetime.now().time() <= dt.time(start_hr,start_min,start_sec):
            sleep(0.5)

        #fetching latest strike and ltp

        if get_closest_val == True:
            print("CLOSEST LOGIC IS TRUE!!")
            ce,pe = closest_val_logic()
            print(ce,pe)
        else:    
            curr_ltp=int(float(ltp_bnf))
            if atm_in_percent == True:
                ce_stk_ltp = (curr_ltp + (ce_atm_percent/100)*curr_ltp)
                pe_stk_ltp = (curr_ltp + (pe_atm_percent/100)*curr_ltp)
            else:
                ce_stk_ltp = curr_ltp + (stk_ce*strike_range)
                pe_stk_ltp = curr_ltp - (stk_pe*strike_range)

            print("CE STRIKE = ",ce_stk_ltp)
            print("PE STRIKE = ",pe_stk_ltp)
            print(curr_ltp)
            ce,pe = int(round(ce_stk_ltp/strike_range)*strike_range), int(round(pe_stk_ltp/strike_range)*strike_range)
            print(strBold('ATM CE '),strLightPurple(ce),strBold(' ATM PE '),strLightPurple(pe))
            #unsubscribing websocket
            unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
            alice.unsubscribe(unsubscribe_list)
            print("UNSUBSCRIBED ",symbol)

        if hedge_ce_position == True:
            buy_ce_hedge()
        
        if hedge_pe_position == True:
            buy_pe_hedge()
        
        #placing our Initial orders,  both CALL and PUT will be sold in this single function : place_orders()
        place_ce_order(ce)
        place_pe_order(pe)
        sleep(2)

        #placing CALL side stoloss order
        place_ce_sl_order()

        #placing PUT side stoloss order
        place_pe_sl_order()
                    
        if target_orders == True:
            place_target_orders()

        if exit_hedge_with_sl_hit == True:
            thread = Thread(target=check_sl_status)
            thread.start()

        if reentry == True:
            run_reentry(ce,pe)
        
        if sl_trail == True:
            run_sl_trail()
        
        if sl_to_cost == True:
            run_sl_to_cost()
            
    except Exception as e:
        err = strRed(e)
        print("Some error occured at intial main:::>",err)
        error = f"{e}"
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("An error ocurred at Line number: ", line_number)
        msg = "Error occurred in "+strategy+" in line number "+str(line_number)+" with error as "+error+ "for client code "+str(client_code)
        send_msg(msg)
        sys.exit()


def run_reentry(ce,pe):
    global max_try_ce, max_try_pe
    print(strLightPurple("WE ARE UNDER REENTRY LOGIC"))
    call_avg_prc_of_the_day = float(ce_sell_avg_p)
    put_avg_prc_of_the_day =float(pe_sell_avg_p) 
    
    while dt.datetime.now().time() < dt.time(exit_hr,exit_min,exit_sec) and reentry == True:
        sleep(2)
        
        ltp_ce = float(get_ltp_info(alice,ins_call))
        ltp_pe = float(get_ltp_info(alice,ins_put))			

        if  order_status(alice,oid_call_slm) == "complete" and ltp_ce <= call_avg_prc_of_the_day and max_try_ce > 0 :
            print("TIME TO PLACE AN REENTRY ORDER CE SIDE")
            place_ce_order(ce)
            place_ce_sl_order()
            max_try_ce -= 1
            

        if  order_status(alice,oid_put_slm) == "complete" and ltp_pe <= put_avg_prc_of_the_day and max_try_pe > 0 :
            print("TIME TO PLACE AN REENTRY ORDER PE SIDE")
            place_pe_order(pe)
            place_pe_sl_order()
            max_try_pe -= 1

        if max_try_ce > 0 and max_try_pe > 0:
            print(strGreen(max_try_ce))
            print(strGreen(max_try_pe))
            print(strRed("THIS IS WORKING"))

def run_sl_trail():
    print(strLightPurple("STARTING SL TRAIL LOGIC"))
    points_to_trail_call = 0.05 * round(float(call_sell_avg_price * call_X_point)/0.05)
    points_to_trail_put = 0.05 * round(float(put_sell_avg_price * put_X_point)/0.05)

    sl_trail_point_call = 0.05 * round(float(slm_call_buy_price * call_Y_point)/0.05)
    sl_trail_point_put = 0.05 * round(float(slm_put_buy_price * put_Y_point)/0.05)

    while dt.datetime.now().time() < dt.time(exit_hr,exit_min,exit_sec) and sl_trail == True:
        sleep(2)
        print("running trail loop")
        # ce_data = alice.get_scrip_info(ins_call)
        # pe_data = alice.get_scrip_info(ins_put)
        # ltp_ce = float(ce_data['Ltp'])
        # ltp_pe = float(pe_data['Ltp'])
        ltp_ce = float(get_ltp_info(alice,ins_call))
        ltp_pe = float(get_ltp_info(alice,ins_put))

        print(float(call_sell_avg_price - ltp_ce))

        if float(call_sell_avg_price - ltp_ce) >=points_to_trail_call and order_status(oid_call_slm) == "trigger pending":
            print("TIME TO MODIFY SLM CE ORDER TO 20 POINTS UP")
            slm_call_buy_price = slm_call_buy_price - sl_trail_point_call
            mod_ce = alice.modify_order(transaction_type = TransactionType.Buy,
                        instrument = ins_call,
                        order_id=oid_call_slm,
                                    quantity = quantity,
                                    order_type = OrderType.StopLossLimit,
                                    product_type = ProductType.Intraday,
                                    price = slm_call_buy_price + 2,
                                    trigger_price = slm_call_buy_price)
            call_sell_avg_price = call_sell_avg_price - points_to_trail_call
            print(call_sell_avg_price,slm_call_buy_price)

        print(float(put_sell_avg_price - ltp_pe))

        if float(put_sell_avg_price - ltp_pe) >=points_to_trail_put and order_status(oid_put_slm) == "trigger pending":
            print("TIME TO MODIFY SLM PE ORDER TO 20 POINTS UP")
            slm_put_buy_price = slm_put_buy_price - sl_trail_point_put
            mod_pe = alice.modify_order(transaction_type = TransactionType.Buy,
                        instrument = ins_put,
                        order_id=oid_put_slm,
                                    quantity = quantity,
                                    order_type = OrderType.StopLossLimit,
                                    product_type = ProductType.Intraday,
                                    price = slm_put_buy_price + 2,
                                    trigger_price =slm_put_buy_price)

            put_sell_avg_price = put_sell_avg_price - points_to_trail_put
            print(put_sell_avg_price,slm_put_buy_price)

        if order_status(oid_call_slm) == "complete" and order_status(oid_put_slm) == "complete":
            exit()

    print("SL TRAIL ENDS HERE")

def place_ce_order(ce):
    global ce_sell_oid,  ins_call

    ins_call = alice.get_instrument_for_fno(exch ='NFO',symbol=trading_symbol,expiry_date=expiry_date,is_fut=False,strike=ce,is_CE=True)
    print(ins_call)
    ce_sell = alice.place_order(transaction_type=ttype,instrument=ins_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
    print(ce_sell)
   

    if ce_sell['stat'] =="Ok":
        print(strGreen("CE ORDER PLACED SUCCESSFULLY!"))
    else:
        for i in range(1):
            print(ce_sell)
            print(strBold("RETRYING TO PLACE ORDER!"))
            ce_sell = alice.place_order(transaction_type=ttype,instrument=ins_call,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
        
            if ce_sell['stat'] =="Ok":
                break
            else:
                print("TRYING AGAIN")

        if ce_sell['stat'] !="Ok":
            print("TRIED 3 Times to place CE Order but still it's not placed. So sending you a message!")
            msg = "CALL ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
            send_msg(msg)
    
    try:
        ce_sell_oid = get_oid(ce_sell)
    except Exception as e:
        print({e})

    
def place_pe_order(pe):
    global  pe_sell_oid,  ins_put
    ins_put = alice.get_instrument_for_fno(exch = 'NFO',symbol=trading_symbol,expiry_date=expiry_date,is_fut=False,strike=pe,is_CE=False)
    pe_sell = alice.place_order(transaction_type=ttype,instrument=ins_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
    print(pe_sell)

    if pe_sell['stat'] =="Ok":
        print(strGreen("PE ORDER PLACED SUCCESSFULLY!"))
    else:
        for i in range(1):
            print(pe_sell)
            print(strBold("RETRYING TO PLACE ORDER!"))
            pe_sell = alice.place_order(transaction_type=ttype,instrument=ins_put,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
            if pe_sell['stat'] =="Ok":
                break
            else:
                print("TRYING AGAIN")
        if pe_sell['stat'] !="Ok":
            print(strRed("TRIED 3 Times to place PE Order but still it's not placed. So sending you a message!"))
            msg = "PUT ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"Statergy : "+strategy
            send_msg(msg)
  
    try:
        pe_sell_oid = get_oid(pe_sell)
    except Exception as e:
        print({e})
    
def place_ce_sl_order():
    global ce_sell_avg_p 

    if order_status(alice,ce_sell_oid) =='rejected':
        ce_sell_avg_p = ap_generator(alice,ce_sell_oid)
        if sl_type =='PERCENT':
            slm_call_buy_price = 0.05 * round((float(ce_sell_avg_p) * sl_ce_value)/0.05)
        else:
            slm_call_buy_price = 0.05 * round((float(ce_sell_avg_p) + sl_ce_value)/0.05)

        slm_limit_call_buy_price = float(round(slm_call_buy_price) + 10)
        sl_call_order = alice.place_order(transaction_type=slttype,instrument=ins_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

        global oid_call_slm

        if sl_call_order['stat'] != 'Ok':
            for i in range(1):
                sl_call_order = alice.place_order(transaction_type=slttype,instrument=ins_call,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_call_buy_price,trigger_price=slm_call_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                if sl_call_order["stat"] == 'Ok':
                    break
                else:
                    print(strBold("RETRYING TO PLACE SLM CALL ORDER ONCE AGAIN"))

            if sl_call_order['stat'] !='Ok':
                msg = "SL CE ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"Statergy : "+ strategy
                send_msg(msg)
        else:
            print(strGreen("CALL SL ORDER PLACED SUCCESSFULLY"))

        try:
            oid_call_slm = get_oid(sl_call_order)
            call_slm_order_status = order_status(alice,oid_call_slm)
            if call_slm_order_status == 'rejected':
                print(strRed("CALL SLM ORDER REJECTED!"))
                msg = "SL CE ORDER REJECTED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
                send_msg(msg)
            else:
                print("Call SLM order placed with status:",strGreen(call_slm_order_status))
        except Exception as e:
            print({e})

    else:
        print(strRed("CALL ORDER REJECTED!"))
        msg= "CALL ORDER REJECTED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
        send_msg(msg)

def place_pe_sl_order():
    global pe_sell_avg_p 

    if order_status(alice,pe_sell_oid) =='rejected':
        pe_sell_avg_p = ap_generator(alice,pe_sell_oid)
        if sl_type =='PERCENT':
            slm_put_buy_price = 0.05 * round((float(pe_sell_avg_p) * sl_pe_value)/0.05)
        else:
            slm_put_buy_price = 0.05 * round((float(pe_sell_avg_p) +  sl_pe_value)/0.05)

        slm_limit_put_buy_price = float(round(slm_put_buy_price) + 10)
        sl_put_order = alice.place_order(transaction_type=slttype,instrument=ins_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

        global oid_put_slm

        if sl_put_order['stat'] != 'Ok':
            for i in range(3):
                sl_put_order = alice.place_order(transaction_type=slttype,instrument=ins_put,quantity=quantity,order_type=OrderType.StopLossLimit,product_type=ProductType.Intraday,price=slm_limit_put_buy_price,trigger_price=slm_put_buy_price,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                if sl_put_order["stat"] == 'Ok':
                    break
                else:
                    print(strBold("RETRYING TO PLACE SLM PUT ORDER ONCE AGAIN"))

            if sl_put_order['stat'] !='Ok':
                msg = "SL PE ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
                send_msg(msg)
        else:
            print(strGreen("PUT SL ORDER PLACED SUCCESSFULLY"))

        try:
            oid_put_slm = get_oid(sl_put_order)
            put_slm_order_status = order_status(alice,oid_put_slm)
            if put_slm_order_status == 'rejected':
                print(strRed("PUT SLM ORDER REJECTED!"))
                msg = "SL PE ORDER REJECTED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
                send_msg(msg)
            else:
                print("Put SLM order placed with status:",strGreen(put_slm_order_status))
        except Exception as e:
            print({e})        
    else:
        print(strRed("PUT ORDER REJECTED!"))
        msg= "PUT ORDER REJECTED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
        send_msg(msg)


def place_target_orders(): 
    global tgt_ce_oid,tgt_pe_oid
    #Target Order details

    if tgt_type =='PERCENT':
        target_ce_price = float(0.05* round((ce_sell_avg_p - (ce_sell_avg_p*ce_tgt_points/100))/0.05))
        target_pe_price = float(0.05* round((pe_sell_avg_p - (pe_sell_avg_p*pe_tgt_points/100))/0.05))
    else:
        target_ce_price = float(0.05* round((ce_sell_avg_p - ce_tgt_points)/0.05))
        target_pe_price = float(0.05* round((pe_sell_avg_p - pe_tgt_points)/0.05))

    ce_target_order = alice.place_order(transaction_type = tgtttype,
                     instrument = ins_call,
                     quantity = quantity,
                     order_type = OrderType.Limit,
                     product_type = ProductType.Intraday,
                     price = target_ce_price,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
    
    pe_target_order = alice.place_order(transaction_type = tgtttype,
                 instrument = ins_put,
                 quantity = quantity,
                 order_type = OrderType.Limit,
                 product_type = ProductType.Intraday,
                 price = target_pe_price,
                 trigger_price = None,
                 stop_loss = None,
                 square_off = None,
                 trailing_sl = None,
                 is_amo = False)

    if ce_target_order['stat'] != 'Ok':
            for i in range(1):
                ce_target_order = alice.place_order(transaction_type = tgtttype,instrument = ins_call,quantity = quantity,order_type = OrderType.Limit,product_type = ProductType.Intraday,price = target_ce_price,trigger_price = None,stop_loss = None,square_off = None,trailing_sl = None,is_amo = False)
                if ce_target_order["stat"] == 'Ok':
                    break
                else:
                    print(strBold("RETRYING TO PLACE TGT CALL ORDER ONCE AGAIN"))

            if ce_target_order['stat'] !='Ok':
                msg = "TGT CE ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
                send_msg(msg)
    else:
        print(strGreen("CALL TGT ORDER PLACED SUCCESSFULLY"))

    if ce_target_order['stat'] != 'Ok':
            for i in range(1):
                pe_target_order = alice.place_order(transaction_type = tgtttype,instrument = ins_put,quantity = quantity,order_type = OrderType.Limit,product_type = ProductType.Intraday,price = target_pe_price,trigger_price = None,stop_loss = None,square_off = None,trailing_sl = None,is_amo = False)
                if pe_target_order["stat"] == 'Ok':
                    break
                else:
                    print(strBold("RETRYING TO PLACE TGT CALL ORDER ONCE AGAIN"))

            if pe_target_order['stat'] !='Ok':
                msg = "TGT PE ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
                send_msg(msg)
    else:
        print(strGreen("PUT TGT ORDER PLACED SUCESSFULLY"))
    
    print("Target for CALL Order is",strLightPurple(target_ce_price),"and Target for PUT Order is",strLightPurple(target_pe_price))
    tgt_ce_oid = get_oid(ce_target_order)
    tgt_pe_oid = get_oid(pe_target_order)


    call_tgt_order_status = order_status(alice,tgt_ce_oid)
    put_tgt_order_status = order_status(alice,tgt_pe_oid)

    if call_tgt_order_status == 'rejected':
        msg = "TGT CE ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
        send_msg(msg)
    
    else:
        print("TGT CE order placed with status:", strGreen(call_tgt_order_status))

    if put_tgt_order_status == 'rejected':
        msg = "TGT PE ORDER NOT PLACED:"+"\n"+"Client: "+client_code+"\n"+"strategy : "+strategy
        send_msg(msg)
    
    else:
        print("TGT PE order placed with status:", strGreen(call_tgt_order_status))

# def check_sl_status():
#     while dt.datetime.now().time() < dt.time(exit_hr,exit_min,exit_sec):
#         if target_orders == False:
#             if order_status(oid_call_slm) == 'complete':
#                 ce_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=call_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
    
#             elif order_status(oid_put_slm) == 'complete':
#                 pe_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=put_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
#         else:
#             if order_status(oid_call_slm) == 'complete' or order_status(tgt_ce_oid) == 'complete':
#                 ce_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=call_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

#             elif order_status(oid_put_slm) == 'complete'  or order_status(tgt_pe_oid) == 'complete':
#                 pe_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=put_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
    

def check_sl_status():
    ce_exit_chance = 1
    pe_exit_chance = 1
    while dt.datetime.now().time() < dt.time(exit_hr,exit_min,exit_sec):

        if exit_hedge_with_sl_hit == True:
            if target_orders == False:
                if order_status(oid_call_slm) == 'complete' and ce_exit_chance > 0:
                    ce_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=call_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                    ce_exit_chance -= 1

                elif order_status(oid_put_slm) == 'complete' and pe_exit_chance > 0:
                    pe_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=put_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                    pe_exit_chance -= 1
            else:
                if (order_status(oid_call_slm) == 'complete' or order_status(tgt_ce_oid) == 'complete') and ce_exit_chance > 0:
                    ce_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=call_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                    print(ce_hedge_exit_order)

                    if order_status(oid_call_slm) == 'complete':
                        # here we will cancel target order
                        print(alice.cancel_order(tgt_ce_oid))
                    else:
                        # here we will cancel SL order
                        print(alice.cancel_order(oid_call_slm))

                    ce_exit_chance -= 1

                elif (order_status(oid_put_slm) == 'complete'  or order_status(tgt_pe_oid) == 'complete')  and pe_exit_chance > 0:
                    pe_hedge_exit_order = alice.place_order(transaction_type=ttype,instrument=put_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
                    print(pe_hedge_exit_order)
                    
                    if order_status(oid_put_slm) == 'complete':
                        # here we will cancel target order
                        print(alice.cancel_order(tgt_pe_oid))
                    else:
                        # here we will cancel SL order
                        print(alice.cancel_order(oid_put_slm))
                        
                    pe_exit_chance -=1

        if target_orders == True and exit_hedge_with_sl_hit == False:

            if order_status(oid_call_slm) == 'complete' and ce_exit_chance > 0 :
                # WE WILL CANCEL TARGET ORDER HERE!
                print(alice.cancel_order(tgt_ce_oid))
                ce_exit_chance -= 1
                # LOGIC NOT COMPLETE NEED TO ADD BREAK AS WE NEED TO MAKE THE CONDITION FALSE AFTER ONE ATTEMPT!!
                
            if order_status(oid_put_slm) == 'complete' and pe_exit_chance > 0:
                # WE WILL CANCEL TARGET ORDER HERE!
                print(alice.cancel_order(tgt_pe_oid))
                pe_exit_chance -= 1


            if order_status(tgt_ce_oid) == 'complete' and ce_exit_chance > 0:
                # WE WILL CANCEL TARGET ORDER HERE!
                print(alice.cancel_order(oid_call_slm))
                ce_exit_chance -= 1

            if order_status(tgt_pe_oid) == 'complete' and pe_exit_chance > 0:
                # WE WILL CANCEL TARGET ORDER HERE!
                print(alice.cancel_order(oid_put_slm))
                pe_exit_chance -= 1
        
def run_sl_to_cost():
    print(strLightPurple("STARTING SL TO COST LOGIC!"))
    while dt.datetime.now().time() < dt.time(exit_hr,exit_min,exit_sec) and sl_to_cost == True:
        sleep(2)

        if order_status(oid_call_slm) == 'complete':
            modify_pe_order_to_cost(alice,ins_put, oid_put_slm,pe_sell_avg_p,quantity)
            sl_to_cost = False

        elif order_status(oid_put_slm) == 'complete':
            modify_ce_order_to_cost(alice,ins_call, oid_call_slm,ce_sell_avg_p,quantity)
            sl_to_cost = False
        

def buy_ce_hedge(curr_ltp):
    global call_hedge_ins

    call_hedge_strike = int(round((curr_ltp + (ce_hedge_strike*strike_range))/strike_range)*strike_range)
    call_hedge_ins = alice.get_instrument_for_fno(exch ='NFO',symbol=trading_symbol,expiry_date=expiry_date,is_fut=False,strike=call_hedge_strike,is_CE=True)
    print(call_hedge_ins)
    hedge_call = alice.place_order(transaction_type=slttype,instrument=call_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
    print(hedge_call)
    
    #getting hedge OID
    global hedge_ce_oid
    hedge_ce_oid = get_oid(hedge_call)
    
def buy_pe_hedge(curr_ltp):
    global put_hedge_ins

    put_hedge_strike = int(round((curr_ltp - (pe_hedge_strike*strike_range))/strike_range)*strike_range)
    put_hedge_ins = alice.get_instrument_for_fno(exch ='NFO',symbol=trading_symbol,expiry_date=expiry_date,is_fut=False,strike=put_hedge_strike,is_CE=False)
    print(put_hedge_ins)
    hedge_put = alice.place_order(transaction_type=slttype,instrument=put_hedge_ins,quantity=hedge_quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
    print(hedge_put)

    #getting hedge OID 
    global hedge_ce_oid
    hedge_pe_oid = get_oid(hedge_put)


def closest_val_logic():
    ce_data = kite.ltp(instrument_ce)
    pe_data = kite.ltp(instrument_pe)

    ltp_ce_list = []
    ltp_pe_list = []
  
    for c in instrument_ce:
        ltp_ce_list.append(ce_data[c]['last_price'])
  
    for p in instrument_pe:
        ltp_pe_list.append(pe_data[p]['last_price'])


    # print(kite.ltp(instrument_ce))
    if closest_type == "NEAR":
        ce_stk = (instrument_ce[closest_value(ltp_ce_list,closest_target_ce)])[-7:-2]
        pe_stk = (instrument_pe[closest_value(ltp_pe_list,closest_target_pe)])[-7:-2]

    if closest_type == "ABOVE":
        ce_stk =(instrument_ce[above_closest_value(ltp_ce_list,closest_target_ce)])[-7:-2]
        pe_stk =(instrument_pe[above_closest_value(ltp_pe_list,closest_target_pe)])[-7:-2]

    if closest_type == "BELOW":
        ce_stk =(instrument_ce[below_closest_value(ltp_ce_list,closest_target_ce)])[-7:-2]
        pe_stk = (instrument_pe[below_closest_value(ltp_pe_list,closest_target_pe)])[-7:-2]

    return ce_stk ,pe_stk


def assigning_variables():
    global socket_opened,trading_symbol,strike_range,q,expiry_date,ttype,slttype,tgtttype,quantity

    socket_opened= False

    if symbol =='NIFTY BANK':
        trading_symbol = 'BANKNIFTY'

    if symbol =='NIFTY 50':
        trading_symbol = 'NIFTY'

    if symbol =='NIFTY FIN SERVICE':
        trading_symbol = 'FINNIFTY'

    if trading_symbol =='BANKNIFTY':
        strike_range = 100
        q = 25

    elif trading_symbol =='NIFTY':
        strike_range = 50
        q = 50

    elif trading_symbol =='FINNIFTY':
        strike_range = 50
        q = 50


    if expiry_type == "Week":
        expiry_date =str(latest_expiry(trading_symbol))
    else:
        expiry_date =str(monthly_expiry(trading_symbol))

    quantity = no_of_lots* q

    if sell_or_buy == "SELL":
        ttype = TransactionType.Sell
        slttype = TransactionType.Buy
        tgtttype = TransactionType.Buy
    else:
        ttype = TransactionType.Buy
        slttype = TransactionType.Sell
        tgtttype = TransactionType.Sell


#Getting All the Necessary Variables

# client_code = us_HUF028.client_code
# full_name = us_HUF028.full_name
# username = us_HUF028.username
# password = us_HUF028.password
# api_key = us_HUF028.api_key
# twoFA = us_HUF028.twoFA
# user_gmail_id = us_HUF028.user_gmail_id
# my_gmail_id = 'hiraninitin96@gmail.com'


api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"       
username = "285915" 

strategy = 'S8-FOUR LOT'
client_code = "HUF028"

symbol = 'NIFTY BANK' #NIFTY BANK, NIFTY 50 ,  NIFTY FIN SERVICE

required_margin = 190000

sell_or_buy = "SELL"

stk_ce = -1 #If ATM then stk = 0 , if OTM1 then change stk to 1(stk=1) if ITM then change the stk to -1 , for ITM use -1,-2,-3,-4,etc and for OTM use 1,2,3,4,etc and for ATM just use 0
stk_pe = -1 #If ATM then stk = 0 , if OTM1 then change stk to 1(stk=1) if ITM then change the stk to -1 , for ITM use -1,-2,-3,-4,etc and for OTM use 1,2,3,4,etc and for ATM just use 0

# no_of_lots = us_HUF028.no_of_lots_four_lot
no_of_lots = 2

sl_type = 'PERCENT' #sl_type can be "PERCENT" or "POINTS"
    
sl_ce_value = 1.15
sl_pe_value = 1.15

start_hr, start_min, start_sec = 9,34,58
print("STARTING TIME IS: ",start_hr,":",start_min,":",start_sec)

exit_hr,exit_min,exit_sec = 15,9,59
print("EXIT TIME IS: ",exit_hr,":",exit_min,":",exit_sec)

expiry_type = "Week" #Month/Eeek
assigning_variables()

##features

reentry = True

max_try_ce = 1
max_try_pe = 1
print(max_try_ce,max_try_pe)

sl_to_cost = False

sl_trail = False
#defining sl trail veriables here for now,
call_X_point,call_Y_point = 0.10, 0.10
put_X_point,put_Y_point = 0.10, 0.10

#Hedges settings:
hedge_ce_position = False
hedge_pe_position = False

hedge_lots = no_of_lots
hedge_quantity = hedge_lots * q

ce_hedge_strike = 7
pe_hedge_strike = 7
exit_hedge_with_sl_hit = False

target_orders = False
tgt_type = "POINTS"
ce_tgt_points = 110
pe_tgt_points = 110


atm_in_percent = True
ce_atm_percent = 1
pe_atm_percent = 1.2


get_closest_val = True
closest_type = "ABOVE" #3 options available -->>    NEAR , ABOVE, & BELOW
closest_target_ce = 100
closest_target_pe = 100


# starting main script

if (__name__=='__main__'):
    # send_msg("TESTING")
    print(strGreen('STARTED STRADDLE'))
    main()














