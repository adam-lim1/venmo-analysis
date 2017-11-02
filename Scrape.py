# ************************** Initialization **************************

from lxml import html
import requests
import pandas as pd
import pandas.io.sql as psql
import pickle
from pandas.io.json import json_normalize
import time

## FUNCTION FOR CONVERTING PAGE TO DATAFRAME
def get_data(json_object):
    
    final_arr = pd.DataFrame()
    for element_num in range(0,len(json_object['data'])):
        my_arr1 = json_normalize(json_object['data'][element_num])
        my_arr2 = json_normalize(json_object['data'][element_num]['transactions'])
        all_cols = pd.concat([my_arr1, my_arr2], axis=1)

        if element_num == 0:
            final_arr = all_cols
        else:
            final_arr = final_arr.append(all_cols)
    
    return final_arr

base_path = 'C:/Users/290002943/Documents/Personal/Venmo Project'

# ************************** Scrape Venmo API **************************

# Define start and end time for scrape vintage
start_unix = 1507584459
end_unix = 1507586529

my_start = start_unix
my_end = start_unix+60

# Step through scrape in minute increments due to number of transaction limitions
while my_start < end_unix:
    page = requests.get('https://venmo.com/api/v5/public?since{}&until={}&limit=1000000'.format(str(my_start), str(my_end)))
    tree = html.fromstring(page.content)
    venmo_trans = get_data(page.json())
    print("{} done".format(my_start))
    
    if (my_start == start_unix):
        all_trans = venmo_trans
    else:
        all_trans = all_trans.append(venmo_trans)
    
    my_start = my_start+60
    my_end = my_end+60
    time.sleep(20)


venmo_trans = all_trans

# Reset index on df
venmo_trans = venmo_trans.reset_index(drop=True)

# write df to file
venmo_trans.to_pickle('{}/Data/venmo_trans.pkl'.format(base_path), compression='infer')