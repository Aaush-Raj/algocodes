from email.message import EmailMessage
import ssl
import smtplib
from alice_blue import *

alice = None
error = "No Errors Found"
print(alice)
gopassive_id  = 'Aaush1002'
username = '28 5915'
password='Test@123'
twoFA='1996'
api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i'
app_id='GNqF2bHlyB'

try:
    access_token = AliceBlue.login_and_get_access_token(username=username,
                                                        password=password,
                                                        twoFA=twoFA,
                                                        api_secret=api_secret,
                                                        app_id=app_id)

    alice = AliceBlue(username=username, password=password,
                    access_token=access_token)
    
except Exception as e:
    error = f"Error:{e}"
    print(error)

    


email_sender = "rajaayush8340@gmail.com"
email_password = 'itniothmjervqxge'
email_receiver = 'aayushcontactinfo@gmail.com'
cc = ['marketalpha07@gmail.com','gopassivemarketing@gmail.com']
# bcc = ['chairman@slayerscouncil.uk']
email_receivers = [email_receiver] + cc 


to = 'aayushcontactinfo@gmail.com'
# cc = 'marketalpha07@gmail.com'
bcc = 'rajayush1024@gmail.com'

subject = "LOGIN DENIED FOR USER: "+username+" UID: "+gopassive_id
body= "Hey! This is to inform you that your Login attempt to aliceblue has been denied by the broker, please check your credentials agian and try! \n" +"Username:"+username+"\nGopassive User Id:"+gopassive_id+"\n"+error
em = EmailMessage()
em['From'] = email_sender
em['To'] = to
em['CC'] = cc
em['Subject']= subject
em.set_content(body)

context = ssl.create_default_context()


if alice == None:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender, [to,cc], em.as_string())
        print("Email sent successfully!")

else:
    print("LOG IN SUCCESSFUL!")
    #final script
