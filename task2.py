from alice_blue import *

import time, datetime

access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
                  access_token=access_token)


instrument_list = ["Nifty Bank"]
socket_opened = False
live_data = {}


def event_handler_quote_update(message):
    live_data[message['instrument'].symbol] = {"Open": message['open'],
                                               "High": message["high"],
                                               "Low": message["low"],
                                               "LTP": message["ltp"],
                                               "Volume": message["volume"],
                                               "Vwap": message["atp"]}


def open_callback():
    global socket_opened
    socket_opened = True


alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)

while not socket_opened:
    print("Connecting to WebSocket...")
    time.sleep(1)
    pass

alice.subscribe([alice.get_instrument_by_symbol("NSE", i) for i in instrument_list], LiveFeedType.MARKET_DATA)


while len(live_data.keys()) != len(instrument_list):
    continue

print("Connected to web socket....")
print(live_data)

while datetime.time(9, 20) >= datetime.datetime.now().time():
    time.sleep(2)
