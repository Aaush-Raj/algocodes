# from threading import Thread
# from time import sleep

# def test():
#     # sleep(60)
#     i = 0
#     while i < 10:
#         i+=1
#         print("WOKRED")

    

# x = "WORKED"
# print("HERE")
# thread = Thread(target=test)
# thread.start()
# print("YESSS")
ce_sell_avg_p = 200
sl_ce_value = 0.1

slm_call_buy_price = 0.05 * round((float(ce_sell_avg_p) * sl_ce_value)/0.05)
print(slm_call_buy_price)