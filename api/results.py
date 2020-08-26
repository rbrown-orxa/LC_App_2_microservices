# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 12:35:17 2020

@author: Sanjeev Kumar
"""

import pandas as pd
import json
from aggregate_loads import (
    get_aggregate_loads,
    get_aggregate_loads_site_pv_optimised)
from optimise_battery import optimise_battery_size
from handle_base_loads import get_base_loads
from handle_ev_loads import get_ev_loads
from utils import get_fixed_fields,get_variable_fields
from optimise_pv import get_optimise_pv_size

def _get_annual_import_site_kwh(schema):
    
     #get base load
     base_load = pd.DataFrame()
     
     #sum base loads
     for load in get_base_loads(schema):
         base_load = load.add(base_load, fill_value=0)
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh = base_load['kWh'].sum()
         
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
         
     return(base_load,annual_cosumption_kwh,import_cost)      
    
         
def _get_annual_import_ev_kwh(schema):
    
     #get ev load
     ev_load = pd.DataFrame()
     
     #sum ev loads
     for load in get_ev_loads(schema):
         ev_load = load.add(ev_load, fill_value=0)
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh = ev_load['kWh'].sum()
     
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
         
     return(ev_load,annual_cosumption_kwh,import_cost)

def _get_annual_import_total_kwh(schema,base_load,ev_load):
    
     aggr_load = base_load + ev_load
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh = aggr_load['kWh'].sum()
     
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
         
     return(aggr_load,annual_cosumption_kwh,import_cost)

def _get_annual_import_with_pv_kwh(schema):
       
     pv_size,sum_load = get_aggregate_loads_site_pv_optimised(schema)   
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh = sum_load['import_kWh'].sum()
     
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']   
       
     return(annual_cosumption_kwh,import_cost,sum_load,pv_size)
 
def _get_annual_import_with_pv_and_battery_kwh(schema,df,pv_size):
        
        curve,size,results=optimise_battery_size(schema,df,pv_size)
        
        cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
        annual_cosumption_kwh = results['P_grid'].sum()
     
        import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
        
        return(size,annual_cosumption_kwh,import_cost)
    

def get_optimise_results(schema):    
    
     #Base load
     (base_load,
        annual_import_site_kwh,
        original_import_cost) = _get_annual_import_site_kwh(schema)
     
     #EV load
     (ev_load,
        annual_import_ev_kwh,
        with_ev_import_cost) = _get_annual_import_ev_kwh(schema)
     
     #Total load
     (aggr_load,
        annual_import_total_kwh,
        total_cost) = _get_annual_import_total_kwh(schema,base_load,ev_load)
     
     #PV optimised load
     (annual_import_with_pv_kwh,
        pv_optimised_cost,
        df,
        pv_size) = _get_annual_import_with_pv_kwh(schema)
     
     #PV and battery optimised load
     (battery_size,
        annual_import_with_pv_and_battery_kwh,
        battery_optimised_cost ) = \
            _get_annual_import_with_pv_and_battery_kwh(
                schema,df,pv_size)
    
     #site results
     
     site = {
            'success': True, 
            'battery_size_kwh': 
                int(battery_size),       
            'annual_import_site_kwh':
                int(annual_import_site_kwh), 
            'annual_import_ev_kwh': 
                int(annual_import_ev_kwh),   
            'annual_import_total_kwh': 
                int(annual_import_total_kwh),
            'annual_import_with_pv_kwh': 
                int(annual_import_with_pv_kwh),
            'annual_import_with_pv_and_battery_kwh': 
                int(annual_import_with_pv_and_battery_kwh),
            'original_import_cost': 
                int(original_import_cost),
            'with_ev_import_cost': 
                int(with_ev_import_cost),
            'total_import_cost': 
                int(total_cost),
            'with_pv_optimised_import_cost': 
                int(pv_optimised_cost),
            'with_battery_optimised_import_cost': 
                int(battery_optimised_cost)
            }
     
     var = get_variable_fields(schema,fields=['name','num_ev_chargers'])
     
     #building results
     buildings = []
     for name,size,num in zip(var['name'],pv_size,var['num_ev_chargers']):
         buildings.append({
            'name':name,
            'pv_size_kw':int(size),
            'num_of_chargers':num})
         
    
     #building result ditionary set
     
     site = {'site':site}
     
     buildings = {'buildings': buildings}
     
     merge = {**site,** buildings}
     
     results = {'results':merge}
    
     return(json.dumps(results))
     
    
if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_optimise_results(request.json))
    
