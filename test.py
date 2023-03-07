from alice_blue import *
import time, datetime
from FNO_details import  nf_ul, nf_nearest, bnf_ul, bnf_nearest


access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@123",
                  access_token=access_token,master_contracts_to_download=['NFO', 'NSE'])

banknifty_nse_index = alice.get_instrument_by_symbol('NSE', 'Nifty Bank')
print(banknifty_nse_index)


# tradingsymbol = "BANKNIFTY"
# banknifty_order = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=datetime.date(2022, 6, 16), is_fut=False, strike=None, is_CE = False)
# print(banknifty_order)
# all_sensex_scrips = alice.search_instruments('NSE', 'NFO')
# print(all_sensex_scrips)
# bn_put = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=datetime.date(2022, 6, 16), is_fut=False, strike=30000, is_CE = False)

# code for checking all positions ---> print(alice.get_netwise_positions())
bn_call = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=datetime.date(2022, 6, 16), is_fut=False, strike=30000, is_CE = True)
print(bn_call)
bn_put = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=datetime.date(2022, 6, 16), is_fut=False, strike=30000, is_CE = False)
print(bn_put)


tradingsymbol = 'BANKNIFTY'
year = 2022
month = 6
date = 16
expiry_date = datetime.date(year,month,date)
latest_strike = float(bnf_nearest)

ce_symbol = alice.get_instrument_for_fno(symbol=tradingsymbol,expiry_date=expiry_date,is_fut=False,strike=latest_strike,is_CE=True)
pe_symbol = alice.get_instrument_for_fno(symbol=tradingsymbol,expiry_date=expiry_date,is_fut=False,strike=latest_strike,is_CE=False)
print(ce_symbol,pe_symbol)

print(alice.place_order(TransactionType.Buy,ce_symbol,1,order_type = OrderType.StopLossLimit,trigger_price = 200,
                     stop_loss = 190,square_off = 190,product_type = ProductType.Intraday))
print(bnf_nearest)

# multiple_underlying = ['BANKNIFTY','NIFTY']
# all_scripts = alice.search_instruments('NFO', multiple_underlying)
# print("NIFTY AND BANK NIFTY DATA LTP-->",all_scripts)


print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%11%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
# print(
#    alice.place_order(transaction_type = TransactionType.Buy,
#                      instrument = alice.get_instrument_by_symbol('NSE', 'INFY'),
#                      quantity = 1,
#                      order_type = OrderType.StopLossLimit,
#                      product_type = ProductType.BracketOrder,
#                      price = 8.0,
#                      trigger_price = 8.0,
#                      stop_loss = 1.0,
#                      square_off = 1.0,
#                      trailing_sl = 20,
#                      is_amo = False)
# )