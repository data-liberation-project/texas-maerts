from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

options = webdriver.ChromeOptions()
options.add_argument('--headless')


import pandas as pd
from io import StringIO

import glob
import os

"""
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆

This script collects metadata for entities that filed a AIR NEW SOURCE PERMITS. 

1. Open a webpage and filter for AIR NEW SOURCE PERMITS and county. 

The script will finish if it's not possible to go through any more zipcodes

ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
"""

import zipcodes
texax_filtered_zips = zipcodes.filter_by(state="TX")

zip_code_index = 0
zip_code_index = 1366
zip_codes = [x['zip_code'] for x in texax_filtered_zips]


"""
pt 2. to see if we miss any zipcodes.
"""

path = "" # use your path
all_files = glob.glob(path)

loaded_files = []
for filepath in all_files:
    df = pd.read_csv(filepath)
    df['zipcode'] = filepath.split("/")[-1].replace(".csv","")
    loaded_files.append(df)

df_p = pd.concat(loaded_files)
remainder_zip_codes = list(set(zip_codes)-set(df_p['zipcode'].unique()))

for zip_code in remainder_zip_codes:
    try:
        
        driver = webdriver.Chrome()
        driver.get("https://www15.tceq.texas.gov/crpub/index.cfm?fuseaction=regent.RNSearch")
        driver.implicitly_wait(5)

        """
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆

        Select base field of AIR NEW SOURCE PERMITS

        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        """

        select_program_type = Select(driver.find_element("name",'pgm_area'))
        select_program_type.select_by_value('AIRNSR    ')
        select_zipcode = driver.find_element(By.XPATH,'//*[@id="zip_cd"]')
                               
        select_zipcode.send_keys(zip_code)

        print(f"Filtering for {zip_code}")
        # submit button
        driver.find_element("name",'_fuseaction=regent.validateRE').click()

        """
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        Extract number of expected records

        Assuming the summary page is structured like
        Your Search Returned 176 Records. To refine your search, click your browser's back button. Click on a column name to change the sort or a RN to view the regulated entity information.
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        """
        
        number_of_records = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/span')
        if number_of_records is None:
            driver.quit()
            continue
        number_of_records_int = int(number_of_records.text)
        total_records = []
        df_total_records = pd.DataFrame()
        """
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        Extract metadata table
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        """

        ## keep clicking until we reach the max pages
        while len(df_total_records)<number_of_records_int:
            df = pd.read_html(StringIO(str(driver.page_source)))[0]
            total_records.append(df)
            df_total_records = pd.concat(total_records)


            try:
                driver.find_element(By.LINK_TEXT, ">").click()
            except:
                break
            sleep(1)

        df_total_records.to_csv(f"../data/regulated_entities/{zip_code}.csv",index=False)

        driver.quit()
    except Exception as e:
        print(e)
        continue

