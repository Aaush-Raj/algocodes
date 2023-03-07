
# importing the module
import pywhatkit
 
# using Exception Handling to avoid
# unprecedented errors
try:
   
  # sending message to receiver
  # using pywhatkit
  pywhatkit.sendwhatmsg("+918340644891",
                        "Hello from Aaush!",
                        15, 52)
  print("Successfully Sent!")
 
except Exception as e:
    print({e})
    # handling exception
    # and printing error message
    print("An Unexpected Error!")