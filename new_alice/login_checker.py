import os
import time
import pandas
import datetime
from pya3 import *
#---------------------------------------------------------------------------------
import gspread  
from oauth2client.service_account import ServiceAccountCredentials
#---------------------------------------------------------------------------------

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\HP\\OneDrive\\Desktop\\algo_trading\\new_alice\\client_secret.json',scope)
client = gspread.authorize(creds)
sheet = client.open('confirm_login').sheet1

dataframe = pd.DataFrame(sheet.get_all_records())

# temp = dataframe.user_id.astype('str').unique().tolist()
all_uid = dataframe.user_id.astype('str').tolist()
all_api_key = dataframe.api_key.astype('str').tolist()

for i in range(len(all_uid)):
    userid = all_uid[i]
    apikey = all_api_key[i]
    alice = Aliceblue(user_id=userid,api_key=apikey)
    session_id = alice.get_session_id()
    if session_id['stat'] =='Ok':
        print("LOGIN WAS SUCESSFULLY DONE FOR",userid)
        dataframe.loc[i, ['login_status']] = 'SUCCESSFULL'
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    else:
        print("LOGIN PENDING FOR",userid)
        dataframe.loc[i, ['login_status']] = 'UNSUCCESSFULL!!!'
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())