from pya3 import *
alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')
print(alice.get_session_id())
import time

LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []

def socket_open():  
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag: 
        alice.subscribe(subscribe_list)

def socket_close(): 
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message): 
    global LTP
    LTP = 0
    print("Error :", message)

def feed_data(message): 
    global LTP, subscribe_flag
    feed_message = json.loads(message)

    
    if feed_message["t"] == "ck":
        subscribe_flag = True
        pass
    elif feed_message["t"] == "tk":
        pass
    else:
        LTP = feed_message[
            'lp'] if 'lp' in feed_message else LTP  
        print(LTP)
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

while not socket_opened:
    pass

subscribe_list = [alice.get_instrument_by_symbol('INDICES', "NIFTY BANK")]
alice.subscribe(subscribe_list)
time.sleep(10)

unsubscribe_list = [alice.get_instrument_by_symbol("INDICES", "NIFTY BANK")]
alice.unsubscribe(unsubscribe_list)


