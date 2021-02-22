#%%
import selenium 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import requests
import json
import os
import time
import numpy as np 

options = Options()
options.headless = True
DRIVER_PATH = '/Applications/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=options)
print('done')

#%%
data_list = []
for i in range(10):
    if i == 0:
        pass
    else:
        driver.get('https://www.compass.com/agents/search-results/?marketId=a0e4100000VIMrBAAX&page=' + str(i) + '&referrer=omnibox')
        time.sleep(1)
        obj = driver.find_elements_by_class_name('agentCard')
        for i in obj:
            data_list.append(i.text)
print(data_list)

#%%
df = pd.DataFrame()
df[0] = data_list
df2 = df[0].str.split('\n',expand=True)

phone_clean = []
for i in df2[2]:
    phone_clean.append(i.replace('M: ', '' ))
df2[3] = phone_clean 
df2.drop(columns = 2, inplace = True)

df2.rename(columns = {0:'Name', 1:'Email', 3:'Phone'}, inplace = True) 

df2.head(10)

#%%
os.mkdir('/Users/ericarsenault/Documents/temp_files')
os.chdir('/Users/ericarsenault/Documents/temp_files')

for i, df in df2.groupby(np.arange(len(df2)) // 100):
    df.to_csv('file' + str(i) + '.csv', index = False) 

folder = os.listdir('/Users/ericarsenault/Documents/temp_files')

print(folder)

#%%
for i in folder:
    url = "http://api.hubapi.com/crm/v3/imports?hapikey=80e60d54-57b3-4221-b524-ab18ec4a1e3a"
    full_path = os.path.abspath(str(i))
    data = {
        "name": str(i),
        "files": [
            {
                "fileName": str(i),
                "fileFormat": "CSV",
                "fileImportPage": {
                    "hasHeader": True,
                    "columnMappings": [
                        {
                            "ignored": False,
                            "columnName": "Name",
                            "idColumnType": None,
                            "propertyName": "firstname",
                            "foreignKeyType": None,
                            "columnObjectType": "CONTACT",
                            "associationIdentifierColumn": False
                        },
                        {
                            "ignored": False,
                            "columnName": "Email",
                            "idColumnType": None,
                            "propertyName": "email",
                            "foreignKeyType": None,
                            "columnObjectType": "CONTACT",
                            "associationIdentifiedColumn": False
                        },
                        {
                            "ignored": False,
                            "columnName": "Phone",
                            "idColumnType": None,
                            "propertyName": "phone",
                            "foreignKeyType": None,
                            "columnObjectType": "CONTACT",
                            "associationIdentifiedColumn": False
                        }
                    ]
                }
            }
        ]}

    datastring = json.dumps(data)

    payload = {"importRequest": datastring}

    files = [
        ('files', open(full_path, 'rb'))
    ]

    response = requests.request("POST", url, data=payload, files=files)
    #Output checking
    print(response.text.encode('utf8'))
    print(response.status_code)

os.remove('/Users/ericarsenault/Documents/temp_files')
driver.quit
print('done')
