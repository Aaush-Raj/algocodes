from alice_blue import *
f = open('C:/Users/HP/OneDrive/Desktop/aliceblue.csv', "r+") 
  
# absolute file positioning
f.seek(0) 
  
# to erase all data 
f.truncate()
print("Operation successful") 


username = "285915"
password="Test@123"
access_token = AliceBlue.login_and_get_access_token(username="285915",
                                                    password="Test@123",
                                                    twoFA='1996',
                                                    api_secret='kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i',
                                                    app_id='GNqF2bHlyB')

# alice = AliceBlue(username=username, password=password,
#                   access_token=access_token)





file1 = open('C:/Users/HP/OneDrive/Desktop/aliceblue.csv',"w")
# L = ["This is Delhi \n","This is Paris \n","This is London \n"]
 
# \n is placed to indicate EOL (End of Line)
file1.write(access_token)
print("Operation to add token successful") 


def generate_access_token(username,password,twoFA,api_secret,app_id):

    access_token = AliceBlue.login_and_get_access_token(username=username,
                                                    password=password,
                                                    twoFA=twoFA,
                                                    api_secret=api_secret,
                                                    app_id=app_id)
    return access_token


generate_access_token('285915','Test@123','1996','kRg5a2cpn0ltTFdMIUhi2MaTuGQkR5oW6VExfIOj29k6oxEgOdujHBzGlNQMru0i','GNqF2bHlyB')
