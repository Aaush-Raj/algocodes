# from flask import Flask
 
# app = Flask(__name__)
 
# @app.route('/')
# def index():
#     return "<h1>Welcome!</h1>"
 
# if __name__ == '__main__':
#    app.run(threaded=True)


# import telegram.ext

# TOKEN = 'AAFB8RZVZOjgjIscsYtCe4ziIZ5RV_5fuhU'

# updater = telegram.ext.updater(TOKEN, use_context = True )
# disp = updater.dispatcher

# def start(update,context):
#     update.message.reply_text("HELLO WELCOME TO AAUSH's PYTHON BOT!")

# def help(update,context):
#     update.message.reply_text("HELLO WELCOME TO AAUSH's PYTHON BOT!")


import requests
# TOKEN = "5627137303:AAFB8RZVZOjgjIscsYtCe4ziIZ5RV_5fuhU"
# grp_chat_id = -783926902

TOKEN = "5660485616:AAEJAVoxdZXXnDnWsipDf4btsFFeHmA1tuc"
grp_chat_id = "983887312"
# url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
# print(requests.get(url).json())
# chat_id = "1108314902"

# grp_chat_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=grp_chat_id&text=grp_msg"
def send_msg(grp_msg):
    grp_chat_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={grp_chat_id}&text={grp_msg}"
    print(requests.get(grp_chat_url).json())

unsuccessful_login_attempts = [1234,5358,4878,15458]
string = """"""
for i in unsuccessful_login_attempts:
     string += (str(i)+'\n')
    
print(string)
grp_msg =  "Login attempt unsuccessful for user id's given below :: \n\n"+ string
send_msg(grp_msg)




# message = "TESTING"
# url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
# print(requests.get(url).json()) # this sends the message

# chat_id = "@algo_testing"
# url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
# requests.get(url).json()




# NITIN SIR CREDENTIALS-->
# tokenbot = "5660485616:AAEJAVoxdZXXnDnWsipDf4btsFFeHmA1tuc"
# chat_id = "983887312"


# import requests

# jokes = ["joke 1", "joke 2", "Joke 3"]

# for joke in jokes:
#  base_url = "https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=-733216636>&text=joke"
#  print("Message is sent")