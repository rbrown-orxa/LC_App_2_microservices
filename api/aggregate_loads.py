# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 11:42:25 2020

@author: Sanjeev Kumar
"""






def get_aggregate_loads(base_load,ev_load):
    
    return(base_load.add(ev_load,fill_value=0))