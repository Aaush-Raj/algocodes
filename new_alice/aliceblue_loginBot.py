import os
import time
import pandas
import datetime
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

file =('C:\\Users\\HP\\OneDrive\\Desktop\\alice_credentials.xlsx')
excel_data_df = pandas.read_excel(file,engine='openpyxl')
print(excel_data_df)
# temp = excel_data_df.user_id.astype('str').unique().tolist()
all_uid = excel_data_df.user_id.astype('str').tolist()
all_pwd = excel_data_df.password.astype('str').tolist()
all_two_FA = excel_data_df.two_FA.astype('str').tolist()

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
        time.sleep(10)
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
        time.sleep(10)
        print("LOGIN SUCCESSFUL")
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/header/div/div/div[2]').click()
        time.sleep(2)
        print("SETTING OPENED")
        
        try:
            driver.find_element(By.XPATH, '//*[@id="list-item-102"]/div[2]/a').click()
        except:
            driver.find_element(By.XPATH, '//*[@id="list-item-96"]/div[1]').click()
            
        driver.find_element(By.XPATH, '//*[@id="app"]/div[4]/div/div/div[3]/button[1]').click()
        print("LOGOUT SUCESSFULLY DONE!!")
        print("<<<--------------------------------------------------------------------------------------->>>")
        time.sleep(3)
        driver.close()
        excel_data_df.loc[i, ['login_status']] = 'SUCCESSFULL'
        excel_data_df.loc[i, ['login_date_and_time']]  = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
        excel_data_df.to_excel(file,index=False)
    except Exception as e:
        print({e})
        excel_data_df.loc[i, ['login_status']] = 'UNSUCCESSFULL!!!'
        excel_data_df.to_excel(file,index=False)
