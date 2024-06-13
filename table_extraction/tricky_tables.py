import os

import pandas as pd
import pdfplumber
import re
import numpy as np


def parse_row(split_line,COLUMNS):
    """
    Read in a list of lines from pdf.text splitted by newline.
    Very customized!! 
    """
        
    remove_white = [x for x in split_line if x != '']    
   
    # when PM has an underscore. It normally gets split as it contains a newline character
    if len(remove_white) == 1 and remove_white[0].isdigit():
        emsource = np.nan
        sourcename = np.nan
        air_cont = remove_white[0]
        lbs_hr = np.nan
        tons_year = np.nan
     # exception case when source name goes beyond character width
    elif len(remove_white) == 1:
        emsource = np.nan
        if len(remove_white[0]) == 1:
            sourcename = np.nan
        else:
            sourcename = remove_white[0]
        air_cont = np.nan
        lbs_hr = np.nan
        tons_year = np.nan
    # ['  PM <0.01', '  0.02']
    elif len(remove_white) == 2 and split_line[0] == '':
        emsource = np.nan
        sourcename = np.nan
        joint_entry = remove_white[0]
        air_cont = joint_entry.split(" ")[2]
        lbs_hr = joint_entry.split(" ")[3]
        tons_year = remove_white[1]
    # [STK 1and STK 2          Dust Collector]
    elif len(remove_white) == 2 and split_line[0] != '':
        emsource = remove_white[0]
        sourcename = remove_white[1]
        air_cont = np.nan
        lbs_hr = np.nan
        tons_year = np.nan

    elif len(remove_white) == 3:
        emsource = np.nan
        sourcename = np.nan
        air_cont = remove_white[0]
        lbs_hr = remove_white[1]
        tons_year = remove_white[2]
    elif len(remove_white) == 4:
        emsource = np.nan
        sourcename = remove_white[0]
        air_cont = remove_white[1]
        lbs_hr = remove_white[2]
        tons_year = remove_white[3]
    # all five values are extractable        
    else:
        emsource = remove_white[0]
        sourcename = remove_white[1]
        air_cont = remove_white[2]
        lbs_hr = remove_white[3]
        tons_year = remove_white[4]

    return pd.DataFrame([[emsource,sourcename,air_cont,lbs_hr,tons_year]],columns=COLUMNS)


def extract_table_custom(lines,COLUMNS):
    total_df = []
    for l in lines:
        split_line = re.split(r'\s{3}', l)
        
        try:
            df = parse_row(split_line,COLUMNS)
            total_df.append(df)
        except Exception as e:
            print(e)
            print(l)
    return pd.concat(total_df)

def clean_up_tricky_table(df_pages):
    """
    Input: Scraped object from pdf page.
    ┌─────────────────── ･ ｡ﾟ★: *.☪ .* :☆ﾟ. ───────────────────────┐

    Two cases to clean up.

    1. Air Contaminant Name	contains an underscore that gets registed as a \n in text. 
    2. Source Name can be long enough that it carries over to the next line.

    Both cases require merging

    └─────────────────── ･ ｡ﾟ★: *.☪ .* :☆ﾟ. ───────────────────────┘
    """

    # Case 1 Air Contaminant Name contains a subscript 
    df_pages['Emission Source'] = df_pages['Emission Source'].ffill()

    groups = df_pages.groupby("Emission Source")
    cleaned_df = []
    for group_name,sample_group in groups:
        sample_group['Emission Rate lbs/hr'] = sample_group['Emission Rate lbs/hr' ].fillna("empty")
        sample_group['Emission Rate tons/year'] = sample_group['Emission Rate tons/year' ].fillna("empty")
        sample_group['Source Name'] = sample_group['Source Name'].fillna("empty")

        try:

            new_rows = []
            for _,row in sample_group.iterrows():
                if row['Emission Rate lbs/hr']=='empty' and row['Emission Rate tons/year']=='empty' and row['Source Name'] == 'empty' and row.name != 0 and row.name != 1:
                    prev_row = new_rows.pop()
                    prev_row['Air Contaminant Name'] = f"{prev_row['Air Contaminant Name']}_{row['Air Contaminant Name']}"
                    new_rows.append(prev_row)
                else:
                    new_rows.append(row)

            df = pd.DataFrame(new_rows)
            cleaned_df.append(df)
        except Exception as e:
            print(group_name)

    df_c = pd.concat(cleaned_df)
    df_c['Source Name'] = df_c['Source Name'].replace("empty",np.nan)
    print(f"Previous Size {len(df_pages)} Cut Down to {len(df_c)}")

    # now merge source namesgroups = df_pages.groupby("Emission Source")
    source_namegroup_df = []
    new_rows = []
    alternate_rows = []
    first_step = False
    for idx,row in df_c.iterrows():
        if row['Emission Rate lbs/hr']=='empty' and row['Emission Rate tons/year']=='empty':
            
            if first_step == False:
                
                # take the main row and store it
                prev_row = new_rows.pop()
                alternate_rows.append(prev_row)
                alternate_rows.append(row)
                first_step = True
            else:
                
                alternate_rows.append(row)
                
        elif len(alternate_rows) > 0:
            
            row_to_alter = alternate_rows[0]
            row_to_alter['Source Name'] = " ".join([str(x['Source Name']) for x in alternate_rows])
            new_rows.append(row_to_alter)
            new_rows.append(row)
            alternate_rows = []
            first_step = False
        else:
            new_rows.append(row)

    df = pd.DataFrame(new_rows)
    source_namegroup_df.append(df)

    df_d = pd.concat(source_namegroup_df)
    print(f"Previous Size {len(df_c)} Cut Down to {len(df_d)}")
    df_d['Source Name'] = df_d['Source Name'].ffill()

    return df_d