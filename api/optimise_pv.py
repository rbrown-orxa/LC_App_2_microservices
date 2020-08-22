# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 12:33:24 2020

@author: Sanjeev Kumar
"""

from aggregate_loads import get_aggregate_loads
from utils import get_form_data,get_generation_1kw,optimise_pv_size


def get_optimise_pv_size(schema):
    
    
    
    fixed_fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost_kwh', 
              'export_price_kwh','pv_cost_kwp', 'pv_life_yrs', 
              'battery_life_cycles', 'battery_cost_kwh',
                   'load_profile_csv_optional']
    
    variable_fields = ['roof_size_m2', 'azimuth_deg','pitch_deg']
   
    form_data = get_form_data(schema,fixed_fields,variable_fields)
    
    list_of_aggr_load = get_aggregate_loads(schema)
    
    list_of_1kw_generation = get_generation_1kw(form_data)
    
    list_of_pv_size,list_of_df = optimise_pv_size(list_of_1kw_generation,list_of_aggr_load,form_data)  
    
    return(list_of_pv_size,list_of_df)
    
    


if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_optimise_pv_size(request.json))