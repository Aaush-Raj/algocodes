from pya3 import *
import datetime
alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')
from time import sleep
session_id = alice.get_session_id()
print(session_id)
# print(alice.get_order_history(''))
print(alice.get_order_history(''))