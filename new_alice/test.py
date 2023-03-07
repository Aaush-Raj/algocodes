# from pya3 import *
# import datetime as dt
# alice = Aliceblue(user_id='285915',api_key='eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9')
# from time import sleep
# session_id = alice.get_session_id()


# import datetime as dt
# def latest_expiry():
# 	global datecalc, call
	
# 	call = False
# 	datecalc = dt.date.today().strftime("%d-%m-%Y") 
# 	while call == False:
# 		try:
# 			sleep(2)
# 			call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datecalc, strike=int(39600), is_CE=True)
# 			print(call)
# 			if call['emsg'] =='No Data':
# 				datecalc = (dt.datetime.strptime(datecalc, "%d-%m-%Y")+  dt.timedelta(days=1)).strftime("%d-%m-%Y")
# 				call = False
# 			else:
# 				call = True
# 		except:
# 			pass
        
# latest_expiry()
# print(datecalc)


import string
import random

# initializing size of string
N = 4
# using random.choices()
# generating random strings
res = ''.join(random.choices(string.ascii_uppercase +string.digits, k=N))

# print result
print("The generated random string : " + (res))
