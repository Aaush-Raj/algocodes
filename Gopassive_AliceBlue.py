from alice_blue import *

import time, datetime

# kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i
# App Secret

# GNqF2bHlyB
# App ID
# username = "285915"
# password = "Test@123"
# twoFA = '1996'
# client_id = 'GNqF2bHlyB'
# client_secret = 'kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i'
# redirect_url = 'https://ant.aliceblueonline.com/plugin/callback/'
access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
#                                                     redirect_url=redirect_url,
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
                  access_token=access_token)
print(alice.get_balance()) # get balance / margin limits
print(alice.get_profile()) # get profile
print(alice.get_daywise_positions()) # get daywise positions
print(alice.get_netwise_positions()) # get netwise positions
print(alice.get_holding_positions()) # get holding positions


instrument_list = ["NFO"]
socket_opened = False
live_data = {}



tradingsymbol = 'BANKNIFTY'
year = 2022
month = 6
date = 16
expiry_date = datetime.date(year,month,date)
latest_strike = 34500.0
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

alice.subscribe([alice.get_instrument_by_symbol(symbol=tradingsymbol,expiry_date=expiry_date,is_fut=False,strike=latest_strike,is_CE=True)], LiveFeedType.MARKET_DATA)


while len(live_data.keys()) != len(instrument_list):
    continue

print("Connected to web socket....")
print(live_data)

while datetime.time(11, 46) >= datetime.datetime.now().time():
    time.sleep(2)

# strategy loop
history = {}
while datetime.time(11, 46) < datetime.datetime.now().time() < datetime.time(11, 47):
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
print("Session Ended !!!!") if datetime.datetime.now().time() > datetime.time(15, 15) else print("Wait till 9:15 !!!!")