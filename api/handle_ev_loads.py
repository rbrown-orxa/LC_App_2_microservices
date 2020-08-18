# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 17:15:30 2020

@author: Sanjeev Kumar
"""

from flask import current_app
import pandas as pd
from datetime import datetime, timedelta



def get_ev_loads(building_type='domestic',ratio=0.2,start_date=None,charge_points=1):
    """
    Get the EV load profile up to one year from start date based on the building type domestic/work/public/commercial/delivery

    
    """
    
    #read the corresponding column building_type, set row = 0 as column names
    df = pd.read_csv(current_app.config['PROFILES_EV'], header=0,usecols=[building_type])
    #get the weekday as offset(0: Monday...6:Sunday)
    offset = datetime.strptime(start_date, '%Y-%m-%d').weekday()
    #Subtract by number days offset so as to align to Monday as start date of EV profile
    start = pd.to_datetime(datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=offset))
    #Set end date to one year later
    end = start + pd.DateOffset(years=1)
    #Multiple EV load by the number of charge points
    building_EV_load_one_year = df * charge_points
    #Generate datetime index of 1 hour frequency
    index = pd.date_range(start=start, end=end, freq='1h')
    #Assign the index to EV load
    building_EV_load_one_year.index = index[0:len(building_EV_load_one_year)]
    
    return(building_EV_load_one_year)


