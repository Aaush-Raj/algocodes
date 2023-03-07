import pywhatkit
from datetime import datetime

# get the current time
now = datetime.now()

# extract the current hour
current_hour = now.hour

# extract the current minute
current_minute = now.minute

print("Current hour:", current_hour)
print("Current minute:", current_minute)

# for i in range(10):
pywhatkit.sendwhatmsg("+918340644891", "HAPPY BIRTHDAY!!🥳🥳", current_hour, current_minute+1)
    # 
    # pywhatkit.sendwhatmsg_instantly(
    # phone_no="+918340644891", 
    # message="Howdy! This message will be sent instantly!",
# )