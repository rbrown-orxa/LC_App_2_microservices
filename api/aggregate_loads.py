# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 11:42:25 2020

@author: Sanjeev Kumar
"""

from handle_base_loads import get_base_loads
from handle_ev_loads import  get_ev_loads



def get_aggregate_loads(schema):
    
    list_of_base_loads = get_base_loads(schema)
    list_of_ev_loads = get_ev_loads(schema)
    
    #Initailise pandas dataframe
    aggr_load = []
    
    for base_load,ev_load in zip(list_of_base_loads,list_of_ev_loads):
        sum_load = base_load.add(ev_load,fill_value=0)
        aggr_load.append(sum_load)
    
    return(aggr_load)   




if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_aggregate_loads(request.json))