from pya3 import *
alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')alice.get_session_id()
print(alice.get_scrip_info(alice.get_instrument_by_token('MCX', 242508)))




















# order =  alice.place_order(transaction_type = TransactionType.Buy,
#                      instrument = alice.get_instrument_by_symbol('NSE', 'INFY'),
#                      quantity = 1,
#                      order_type = OrderType.Market,
#                      product_type = ProductType.Delivery,
#                      price = 0.0,
#                      trigger_price = None,
#                      stop_loss = None,
#                      square_off = None,
#                      trailing_sl = None,
#                      is_amo = False,
#                      order_tag='order1')

# oid_call = order['NOrdNo']
# print(oid_call)
# call_order_details = alice.get_order_history(oid_call)
# call_order_status = call_order_details['Status']
# call_sell_avg_price = call_order_details['Avgprc']

# print(call_order_details)
# print(call_order_status)
# print(call_sell_avg_price)