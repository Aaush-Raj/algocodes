# from test_algo import user_creds
from test_algo import *
import sys
from common_functions import * 

username = '285915'
api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'

alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())

print(get_date_curr_expriry(42600))
print(latest_expiry(alice))

# username = '285915'
# api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'


# try:
#     print(username,api_key)
#     print(user_creds(username,api_key))
#     print(main())

# except Exception as e:
#     print(e)
#     exception_type, exception_object, exception_traceback = sys.exc_info()
#     filename = exception_traceback.tb_frame.f_code.co_filename
#     line_number = exception_traceback.tb_lineno
#     print(line_number)
#     print("THIS")
