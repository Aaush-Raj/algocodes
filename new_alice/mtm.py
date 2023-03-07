from pya3 import *

# username = '285915'
# api_key = 'eUmxHh0mSZujQ4xGn2Bi5BOgDtVoalyG4ssEzPmFeJy0d0ocPtRhCYC3xZyRZ4S2DPfUq4DsHQxcLqPjnG0CNht5Y1Y5e8XrP8zB97G4ocBf7hljkKKNfsmHyWu2BFb9'
username = '612538'
api_key = 'geLpR5rUz5YzPeXzoPUjya2mmjyVfbQpgyF0Qm2QZpaMG7yhBRFnFTI2bJ3LFeUO0p1FFQtL0vT2cnAdIR23Dfp6bOU3KyG5lxhuxMC9XItBZkyGfUpqGy4GxsTh1Tix'
alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())


print(alice.get_netwise_positions())


#This version of autologin works for TOTP Login.

import os
import sys
import pandas as pd
from pya3 import *
import time
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\myfiles\\clientdata\\loginautomation.json',scope)
client = gspread.authorize(creds)
sheet = client.open('clientdata').sheet1
sheet2 = client.open('clientdata').worksheet('MTM')

dataframe = pd.DataFrame(sheet.get_all_records())
dataframe2 = pd.DataFrame(sheet2.get_all_records())


# temp = dataframe.user_id.astype('str').unique().tolist()
all_uid = dataframe.user_id.astype('str').tolist()
all_api_key = dataframe.api_key.astype('str').tolist()
all_client_id = dataframe.client_id.astype('str').tolist()
all_Name = dataframe.Name.astype('str').tolist()
all_active_status = dataframe.active.astype('str').tolist()


for i in range(len(all_uid)):
    print(i)
    userid = all_uid[i]
    apikey = all_api_key[i]
    client_id = all_client_id[i]
    name = all_Name[i]
    active = all_active_status[i]


    print(userid)
    alice = Aliceblue(user_id=userid,api_key=apikey)
    print(alice.get_session_id())


    if active =='yes':
        date_today = datetime.datetime.now().strftime("%d/%m/%y")
        netwise_positions = alice.get_netwise_positions()
        MTM = 0
        for i in range(len(netwise_positions)):
            m = (netwise_positions[i]['MtoM'])
            print(m)
            MTM += (float(m.replace(',','')))

        dataframe2.loc[i, ['client_id']] = client_id
        dataframe2.loc[i, ['Name']] = name
        dataframe2.loc[i, ['user_id']] = userid
        dataframe2.loc[i, ['date']] = date_today
        dataframe2.loc[i, ['MTM']] = MTM
        sheet2.update([dataframe2.columns.values.tolist()] + dataframe2.values.tolist())

        
        
    else:
        print("error with this user",userid)
        dataframe2.loc[i, ['date']] = None
        dataframe2.loc[i, ['MTM']] = 'NULL'
        sheet2.update([dataframe2.columns.values.tolist()] + dataframe2.values.tolist())

