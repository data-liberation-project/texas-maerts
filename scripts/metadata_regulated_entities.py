from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


import pandas as pd
from io import StringIO

"""
ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆

This script collects metadata for entities that filed a AIR NEW SOURCE PERMITS. 

1. Open a webpage and filter for AIR NEW SOURCE PERMITS and county. 

The script will finish if it's not possible to select any more counties. 

ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
"""

county_index = 254

while True:
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
        select_county= Select(driver.find_element("name",'cnty_name'))

        # 0 is not a valid option, so we start at 1.

        county_name_selection = select_county.select_by_index(county_index)
        selected_option_text = select_county.first_selected_option.text
        print(f"Filtering for {selected_option_text} and idx {county_index}")
        driver.find_element("name",'_fuseaction=regent.validateRE').click()

        """
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        Extract number of expected records

        Assuming the summary page is structured like
        Your Search Returned 176 Records. To refine your search, click your browser's back button. Click on a column name to change the sort or a RN to view the regulated entity information.
        ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆ଘ( ･ω･)_/ﾟ･:*:･｡☆
        """
        number_of_records = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/span')
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

        df_total_records.to_csv(f"../data/regulated_entities_county/{selected_option_text}.csv",index=False)

        driver.quit()
        county_index = county_index + 1
    except Exception as e:
        print(e)
        county_index = county_index + 1
        continue

