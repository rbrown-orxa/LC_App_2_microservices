# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 17:15:30 2020

@author: Sanjeev Kumar
"""

import pandas as pd
from datetime import datetime, timedelta
import config as cfg
import logging

from utils import get_variable_fields


def get_ev_loads(schema):
    
    list_of_ev_loads=[]
    dict = get_variable_fields(
        schema,
        fields=['num_ev_chargers','building_type'])
    building_type = dict['building_type']  
    no_of_ev_chargers = dict['num_ev_chargers']   
    for btype,no_ev_charger in zip(
                                    building_type,
                                    no_of_ev_chargers):
        list_of_ev_loads.append(_process_ev_load(
            building_type=btype,
            charge_points=no_ev_charger ))
        
    return(list_of_ev_loads)


def _process_ev_load(
        building_type='domestic',
        ratio=0.2,
        start_date=None,
        charge_points=1):
    """
    Get the EV load profile up to one year from start date 
    based on the building type domestic/work/public/commercial/delivery
    """
    
    #read the corresponding column building_type, set row = 0 as column names
    df = pd.read_csv(cfg.PROFILES_EV, header=0,usecols=[building_type])
    
    if start_date is not None:
        #get the weekday as offset(0: Monday...6:Sunday)
        offset = datetime.strptime(start_date, '%Y-%m-%d').weekday()
        #Subtract by number days offset so as to align to Monday 
        #as start date of EV profile
        start = pd.to_datetime(
            datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=offset))
        #Set end date to one year later
        end = start + pd.DateOffset(years=1)
        #Generate datetime index of 1 hour frequency
        index = pd.date_range(start=start, end=end, freq='1h')
        #Multiply EV load by the number of charge points
        building_EV_load_one_year = df * charge_points
        #Assign the index to EV load
        building_EV_load_one_year.index = \
            index[0:len(building_EV_load_one_year)]
    else:        
        #Multiply EV load by the number of charge points
        building_EV_load_one_year = df * charge_points        
        #rename the column
        building_EV_load_one_year.rename(
            columns={building_type:'kWh'},
            inplace=True)
        #rename the index as hours
        building_EV_load_one_year.index.name='hours'                                 
    
    return(building_EV_load_one_year)


if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_ev_loads(request.json))
