from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException,WebDriverException


import pandas as pd
from io import StringIO

import glob
import os
import shutil
import time


import os
from dotenv import load_dotenv

load_dotenv()

"""
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆

ENV Variables
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
"""

# # csv file of registered entities scraped by zipcode
# ZIPCODE_LOCATION = os.getenv('ZIPCODE_LOCATION')
# # csv file of registered entities scraped by county
# COUNTY_LOCATION = os.getenv('COUNTY_LOCATION')

JOINED_DATA_LOCATION = os.getenv('JOINED_DATA_LOCATION')
# users general download folder
DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')
# new location for MAERT pdfs.
NEW_MAERT_LOCATION = os.getenv('NEW_MAERT_LOCATION')
 
"""
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆

This script collects MAERT for RNs found with metadata_regulated_entities zipcode.py and metadata_regulated_entities.py.

It will click the download link 

Note that the set of RN_collected is a subset of RN_total. There exists RN not associated with zipcode/county.

ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
"""
"""
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆

Useful Functions

ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
"""

def read_in_csv_directory(path):
    all_files = glob.glob(path)

    loaded_files = []
    for filepath in all_files:
        df = pd.read_csv(filepath)
        loaded_files.append(df)

    df_p = pd.concat(loaded_files)

    return df_p


"""
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆

Create mega df to search RNs.

ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
"""

# df_zipcode = read_in_csv_directory(ZIPCODE_LOCATION)
# df_county = read_in_csv_directory(COUNTY_LOCATION)

# df_joined = pd.concat([df_zipcode,df_county]).drop_duplicates()
df_joined = read_in_csv_directory(JOINED_DATA_LOCATION)
df_joined.columns = ['rn_number','regulated_entity_name','county','location']

"""
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆cccccbctljbufdhvedjjrrjgfbbiltitvglkgkfnntib


Trawl through each RN

ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
"""

## this is used to begin from last collection point. it's a doozy to collect.
rn_numbers = list(df_joined['rn_number'].unique())
idx = rn_numbers.index("RN102198850")
#RN106478944 tricky bug?
#RN102563327
print(idx)

for rn in rn_numbers[idx+1:]:
    print(f"Searching for {rn}")

    try:
        """
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        The following code downloads a particular MAERT file directly to the downloads folder. 
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        """

        driver = webdriver.Chrome()
        driver.get("https://records.tceq.texas.gov/cs/idcplg?IdcService=TCEQ_SEARCH")
        driver.implicitly_wait(5)


        select_program_type = Select(driver.find_element(By.XPATH,'//*[@id="xRecordSeries"]'))
        #AIR / New Source Review Permit
        select_program_type.select_by_value('1081')

        select_secondary_criteria = Select(driver.find_element(By.XPATH,'/html/body/table[1]/tbody/tr[5]/td/table/tbody/tr/td/div/form/table/tbody/tr[4]/td/table/tbody/tr[1]/td[1]/select'))
        #Central Registry RN
        select_secondary_criteria.select_by_value('xRefNumTxt')

        select_rn = driver.find_element(By.XPATH,'/html/body/table[1]/tbody/tr[5]/td/table/tbody/tr/td/div/form/table/tbody/tr[4]/td/table/tbody/tr[1]/td[2]/input')      
        select_rn.send_keys(rn)

        #click search
        driver.find_element(By.XPATH, "/html/body/table[1]/tbody/tr[5]/td/table/tbody/tr/td/div/form/table/tbody/tr[4]/td/table/tbody/tr[5]/td[3]/div/button[1]").click()

        while True:
            df = pd.read_html(StringIO(str(driver.page_source)))
            """
            This section is done by manually finding out the nuances of the table data. 
            """
            table_of_data = df[4]

            maert_table = table_of_data[table_of_data[12]=='MAERT']
            hyperlinks = maert_table[2].values
            permit_numbers = maert_table[6].values
            dates = maert_table[16].values

            for hyperlink,permit_number,date in zip(hyperlinks,permit_numbers,dates):
                driver.find_element(By.LINK_TEXT, hyperlink).click()
                time.sleep(10)
                list_of_files = glob.glob(DOWNLOAD_FOLDER) # * means all if need specific format then *.csv
                latest_file = max(list_of_files, key=os.path.getatime)
                unique_id = int(time.time())
                date_modified = date.split(" ")[0].replace("/","-")
                new_file_location = f"{NEW_MAERT_LOCATION}/{rn}_{permit_number}_{date_modified}_{unique_id}.pdf"
                shutil.move(latest_file,new_file_location)
                print(f"Moved File to {new_file_location}")

            try:
                driver.find_element(By.XPATH,"/html/body/table[1]/tbody/tr[5]/td/table/tbody/tr/td/div/div[2]/table/tbody/tr/td[5]/a").click()
            except WebDriverException:
                print("No more pages left!")
                driver.quit()
                break
    except Exception as e:
        print(e)
        driver.quit()
        continue