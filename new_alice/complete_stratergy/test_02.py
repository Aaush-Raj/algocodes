from alice_blue import *
import sys
import math
import time
import datetime
from datetime import date,timedelta


def round_nearest(x, num=50): return int(round((x/100))*100)
def nearest_strike_bnf(x): return round_nearest(x, 100)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)



access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@1234",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

alice = AliceBlue(username='285915', password="Test@1234",
                  access_token=access_token)

x = alice.get_order_history();

print(len(x))
# print(x['completed_orders'])
# print(x['pending_orders'])
print(x['data'])