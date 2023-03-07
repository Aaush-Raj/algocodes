api_key = "eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9"       
user_id = "285915"         

from AliceBlue_V2 import Alice

alice = Alice(user_id=user_id, api_key=api_key)
print(alice.create_session())       # Must "log in" to Alice platform before create session
alice.download_master_contract(to_csv=True)         # Download initially once a day
import datetime
from datetime import date
import time

socket_opened = False


def event_handler_quote_update(message):
    ltp_bnf = message['lp']
    print("LATEST BANKNIFTY STRIKE IS-->",ltp_banknifty)
    # print(message)


def open_callback():
    global socket_opened
    socket_opened = True


alice.invalidate_socket_session()
alice.create_socket_session()
alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)
while not socket_opened:
    pass
print("Websocket : Connected")
alice.subscribe([alice.get_instrument_by_symbol("NSE", i) for i in ["LUPIN-EQ"]])
time.sleep(30)
# alice.unsubscribe([alice.get_instrument_by_symbol("NSE", i) for i in ["ACC-EQ", "RELIANCE-EQ"]])
time.sleep(10)
