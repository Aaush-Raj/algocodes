from pya3 import *
import datetime
from datetime import date
alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')

print(alice.get_session_id())
# alice.get_contract_master("MCX")
alice.get_contract_master("NFO")
alice.get_contract_master("NSE")
# print(alice.get_instrument_by_token("MCX",239484))
expiry_date = date(2022,8,11)
# bn_pe_trade = alice.get_instrument_for_fno(symbol='BANKNIFTY', expiry_date=expiry_date, is_fut=False, strike=35000, is_CE=False)
trade = alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="11-08-2022", is_fut=True,strike=None, is_CE=False)
print(trade)