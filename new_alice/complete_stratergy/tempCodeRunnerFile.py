
call =None
call = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date="22-08-2022", strike=39600, is_CE=True)
print(call)

if call == None:
    print("TRUE")
else:
    print("CALL FALSE")