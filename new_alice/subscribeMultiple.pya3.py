from time import sleep
from pya3 import *
import datetime
alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')
from time import sleep
session_id = alice.get_session_id()


bnf_call_ltp = 0
bnf_put_ltp = 0
ltp_bnf = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []
symbol = 'Nifty 50'
# symbol2 = 'BANKNIFTY'
# symbol2 = 'Nifty 50'
symbol2 = 'NIFTY BANK'



def socket_open():  # Socket open callback function
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
        alice.subscribe(subscribe_list)

def socket_close():  # On Socket close this callback function will trigger
    global socket_opened, ltp_bnf,bnf_call_ltp,bnf_put_ltp
    socket_opened = False
    ltp_bnf = 0
    bnf_put_ltp = 0
    bnf_call_ltp= 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global ltp_bnf,bnf_call_ltp,bnf_put_ltp
    ltp_bnf = 0
    bnf_put_ltp = 0
    bnf_call_ltp = 0
    print("Error :", message)

def feed_data(message):  
    global ltp_bnf,bnf_call_ltp,bnf_put_ltp, subscribe_flag
    feed_message = json.loads(message)
    if feed_message["t"] == "ck":
        subscribe_flag = True
        pass
    elif feed_message["t"] == "tk":
        pass
    else:

        if feed_message['tk'] == str(token_bnf_call):
            print(token_bnf_call)
            bnf_call_ltp = feed_message['lp'] if 'lp' in feed_message else bnf_call_ltp
            print("BNF CALL LTP -->",bnf_call_ltp)
        
        elif feed_message['tk'] == str(token_bnf_put):
            print(token_bnf_call)
            bnf_put_ltp = feed_message['lp'] if 'lp' in feed_message else bnf_put_ltp
            print("BNF PUT LTP -->",bnf_put_ltp)
        else:
            ltp_bnf = feed_message['lp'] if 'lp' in feed_message else ltp_bnf  
            print(ltp_bnf)
            
# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

while not socket_opened:
    pass
subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
alice.subscribe(subscribe_list)
sleep(10)

sleep(2)
print("SUBSCRIBED")
unsubscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
alice.unsubscribe(unsubscribe_list)

bnf_call = alice.get_instrument_for_fno(exch = 'NFO',symbol='NIFTY',expiry_date="2022-09-22",is_fut=False,strike=17900,is_CE=True)
bnf_put = alice.get_instrument_for_fno(exch = 'NFO',symbol='NIFTY',expiry_date="2022-09-22",is_fut=False,strike=17700,is_CE=False)
token_bnf_call = bnf_call[1]
token_bnf_put = bnf_put[1]


# print(token_bnf_call)
subscribe_list = [bnf_call,bnf_put]
alice.subscribe(subscribe_list)
print("SUBSCRIBED AGAIn")
sleep(10)

sleep(2)

unsubscribe_list = [bnf_call,bnf_put]
alice.unsubscribe(unsubscribe_list)

print("BNF PUT LTP00 -->",bnf_put_ltp)
print("BNF CALL LTP 00-->",bnf_call_ltp)