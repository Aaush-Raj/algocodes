from alice_blue import *

import time, datetime


access_token = AliceBlue.login_and_get_access_token(username="user_id",
                                                    password='password',
                                                    twoFA='two_fa',
                                                    api_secret="api_secret",
                                                    app_id="api_key")

alice = AliceBlue(username="user_id", password='password',
                  access_token="access_token")

instrument_list = ["ACC", "ADANIENT", "UPL", "PNB"]
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

# strategy loop
history = {}
while datetime.time(9, 20) < datetime.datetime.now().time() < datetime.time(15, 15):
    for symbol, values in live_data.items():
        try:
            history[symbol]
        except:
            history[symbol] = {"High": values["High"], "Low": values["Low"], "Traded": False}
        if values['High'] > history[symbol]['High'] and values["Open"] == values['Low'] and not history[symbol]['Traded']:
            print("Buy :", symbol, f" at {values['High']} and Time {datetime.datetime.now().time()}")
            history[symbol]['Traded'] = True
        if values['Low'] < history[symbol]['Low'] and values["Open"] == values['High'] and not history[symbol]['Traded']:
            print("Sell :", symbol, f" at {values['Low']} and Time {datetime.datetime.now().time()}")
            history[symbol]['Traded'] = True
    time.sleep(2)
print("Session Ended !!!!") if datetime.datetime.now().time() > datetime.time(15, 15) else print("Wait till 9:20 !!!!")