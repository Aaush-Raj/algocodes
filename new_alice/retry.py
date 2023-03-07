api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"       
user_id = "285915"    
from time import sleep
import datetime as dt
from pya3 import *
alice = Aliceblue(user_id=user_id,api_key=api_key)
print(alice.get_session_id())



def retry(instrument,retry_typ,ttype,quantity,price,tgp):
    retry = 2
    slm_retry = 2
    print(retry_typ)

    if retry_typ == 'normal':
        print("NRLM ORD")
        while retry != 0:
            sleep(2)
            if ttype == 'Sell':
                ord = alice.place_order(transaction_type=TransactionType.Sell,instrument=instrument,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
            else:
                ord = alice.place_order(transaction_type=TransactionType.Buy,instrument=instrument,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)


            if ord["stat"] == "Not_ok":
                print("Retry->",retry)
                retry -= 1
            else:
                break

        if ord["stat"] == "Not_ok":
            print("Tried 2 times but still order not placed")
        else:
            print("Order placed successfully!")

    elif retry_typ == 'tgt':
        print("TGT ORD")
        while retry != 0:
            sleep(2)
            if ttype == 'Sell':
                tgt_ord = alice.place_order(transaction_type=TransactionType.Sell,instrument=instrument,quantity=quantity,order_type=OrderType.Limit,product_type = ProductType.Intraday,price = price,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
            else:
                tgt_ord = alice.place_order(transaction_type=TransactionType.Buy,instrument=instrument,quantity=quantity,order_type=OrderType.Limit,product_type = ProductType.Intraday,price = price,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

            
            if tgt_ord["stat"] == "Not_ok":
                retry -= 1
            else:
                print(tgt_ord["stat"])
                break

        if tgt_ord["stat"] == "Not_ok":
            print("Tried 2 times but still order not placed")
        else:
            print("Order placed successfully!")

    else:
        while retry != 0:
            print("SLM ORD")
            sleep(2)
            if ttype == 'Sell':
                slm_ord = alice.place_order(transaction_type=TransactionType.Sell,instrument=instrument,quantity=quantity,order_type=OrderType.StopLossLimit,product_type = ProductType.Intraday,price = price,trigger_price=tgp,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
            else:
                slm_ord = alice.place_order(transaction_type=TransactionType.Buy,instrument=instrument,quantity=quantity,order_type=OrderType.StopLossLimit,product_type = ProductType.Intraday,price = price,trigger_price=tgp,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)

            if slm_ord["stat"] == "Not_ok":
                retry -= 1
            else:
                break
        if sell_order_call["stat"] == "Not_ok":
            print("Tried 2 times but still order not placed")
        else:
            print("Order placed successfully!")



quantity = 25
ce = 39000
instrument  = alice.get_instrument_for_fno(exch='NFO',symbol='BANKNIFTY',expiry_date="2022-10-13",is_fut=False,strike=39000,is_CE=True)
print(instrument)
sell_order_call = alice.place_order(transaction_type=TransactionType.Sell,instrument=instrument,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Intraday,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
if sell_order_call["stat"] == "Not_ok":
# if sell_order_call["stat"] != "Not_ok": for testing when session is already created
    print("ORDER NOT PLACED")
    retry(instrument,'tgt','Buy',quantity,490.0,None) #for tgt order
    retry(instrument,'slm','Sell',quantity,440.0,430.0)    #for slm order
    retry(instrument,'normal','Buy',quantity,None,None)    #for norml order