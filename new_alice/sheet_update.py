import os
import time
import pandas as pd
import pandas
import datetime
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#---------------------------------------------------------------------------------
import gspread  
from oauth2client.service_account import ServiceAccountCredentials
#---------------------------------------------------------------------------------

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\HP\\OneDrive\\Desktop\\algo_trading\\new_alice\\client_secret.json',scope)
client = gspread.authorize(creds)
sheet = client.open('python_test').sheet1

dataframe = pd.DataFrame(sheet.get_all_records())

def launch_driver(driver_path: str):
    options = webdriver.ChromeOptions()
    options.add_argument('no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    # Set screen size to 1080p
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    options.headless = False
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

path = ChromeDriverManager(path=os.getcwd()).install()

# temp = dataframe.user_id.astype('str').unique().tolist()
all_uid = dataframe.user_id.astype('str').tolist()
all_pwd = dataframe.password.astype('str').tolist()
all_two_FA = dataframe.two_FA.astype('str').tolist()

print(all_uid)
print(all_pwd)
print(all_two_FA)
for i in range(len(all_uid)):
    url = "https://a3.aliceblueonline.com"
    userid = all_uid[i]
    password = all_pwd[i]
    two_FA = all_two_FA[i]
    print(userid)
    print(password)
    print(two_FA)
    try:    
        driver = launch_driver(path)
        driver.get(url)
        time.sleep(5)
        print("STARTS")
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/form/div/input').send_keys(userid)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/form/button').click()
        time.sleep(5)
        input_requirement_text = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/form/div/label').text
        print(input_requirement_text)
        if input_requirement_text == 'M-Pin':
            driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/div[1]/span[1]').click()
            time.sleep(2)
        else:
            pass
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/form/div/div[1]/span[1]/input').send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/form/button').click()
        time.sleep(7)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/form/div/div[1]/span[1]/input').send_keys(two_FA)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[1]/div[2]/form/button').click()
        time.sleep(5)
        print("LOGIN SUCCESSFUL")
        time.sleep(7)
       
        driver.close()
        dataframe.loc[i, ['login_status']] = 'SUCCESSFULL'
        dataframe.loc[i, ['login_date_and_time']]  = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    except Exception as e:
        print({e})
        dataframe.loc[i, ['login_status']] = 'UNSUCCESSFULL!!!'
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())