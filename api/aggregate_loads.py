# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 11:42:25 2020

@author: Sanjeev Kumar
"""

from handle_base_loads import get_base_loads
from handle_ev_loads import  get_ev_loads
import pandas as pd
import sys
import logging

import optimise_pv
import utils

def get_aggregate_loads(schema):
    # utils.call_trace()
    
    list_of_base_loads = get_base_loads(schema)
    list_of_ev_loads = get_ev_loads(schema)
    
    #Initailise pandas dataframe
    aggr_load = []
    
    for base_load,ev_load in zip(list_of_base_loads,list_of_ev_loads):
        sum_load = base_load.add(ev_load,fill_value=0)
        aggr_load.append(sum_load)
    
    return(aggr_load)
    

# <<<<<<< HEAD
# def get_aggregate_loads_site(schema):

# =======
def get_aggregate_loads_site_pv_optimised(schema):
# >>>>>>> master
    
    pv_size,aggr_load = optimise_pv.get_optimise_pv_size(schema) # Call the API
    
    for load in aggr_load:
        load.rename(columns={load.columns[0]:'gen_kwh'},inplace=True)
    
    #Initailise pandas dataframe
    aggr_load_site = pd.DataFrame()
    
    for load in aggr_load:
        aggr_load_site = load.add(aggr_load_site, fill_value=0)  
    
    return(pv_size,aggr_load_site)



if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_aggregate_loads(request.json))
    
# <<<<<<< HEAD
#     print(get_aggregate_loads_site(request.json))




# =======
    print(get_aggregate_loads_site_pv_optimised(request.json))
# >>>>>>> master
