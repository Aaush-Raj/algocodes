from pya3 import *

# username = "285915"
# password="Test@123"
# access_token = open('C:/Users/HP/OneDrive/Desktop/aliceblue.csv','r').read().strip()
# alice = AliceBlue(username=username, password=password,
#                   access_token=access_token)
# print("ACCESS TOKEN",access_token)


alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')

print(alice.get_session_id()) # Get Session ID
print(alice.get_balance()) # get balance / margin limits
print(alice.get_profile()) # get profile