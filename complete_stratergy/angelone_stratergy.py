from smartapi import SmartConnect
# apikey = 'oFrFjeSe'
# clientId = 'L53854'
# password = 'hemu9829'
# @Rajaayush1
apikey = 'GHs4KzGv'
clientId = 'A718575'
password = '@ankitraj1'
# @Rajaayush1
obj=SmartConnect(api_key=apikey)
data = obj.generateSession(clientId,password)
print(data)
refreshToken= data['data']['refreshToken']
print(refreshToken)
feedToken=obj.getfeedToken()
userProfile= obj.getProfile(refreshToken)


try:
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "19500",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
        }
    orderId=obj.placeOrder(orderparams)
    print("The order id is: {}".format(orderId))
except Exception as e:
    print({e})
#     print("Order placement failed: {}".format(e.message))

from smartapi import SmartWebSocket

# feed_token=092017047
FEED_TOKEN=feedToken
CLIENT_CODE=clientId
# token="mcx_fo|224395"
token=" nse_cm|13611"    #SAMPLE: nse_cm|2885&nse_cm|1594&nse_cm|11536&nse_cm|3045
# token="mcx_fo|226745&mcx_fo|220822&mcx_fo|227182&mcx_fo|221599"
task="mw"   # mw|sfi|dp

ss = SmartWebSocket(FEED_TOKEN, CLIENT_CODE)

def on_message(ws, message):
    print(message)
    print("Ticks: {}".format(message))
    
def on_open(ws):
    print("on open")
    ss.subscribe(task,token)
    
def on_error(ws, error):
    print(error)
    
def on_close(ws):
    print("Close")

# Assign the callbacks.
ss._on_open = on_open
ss._on_message = on_message
ss._on_error = on_error
ss._on_close = on_close

ss.connect()