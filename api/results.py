# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 12:35:17 2020

@author: Sanjeev Kumar
"""

import pandas as pd
import json
from aggregate_loads import get_aggregate_loads,get_aggregate_loads_site
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
         
     return(annual_cosumption_kwh,import_cost)      
    
         
def _get_annual_import_ev_kwh(schema):
    
     #get ev load
     ev_load = pd.DataFrame()
     
     #sum ev loads
     for load in get_ev_loads(schema):
         ev_load = load.add(ev_load, fill_value=0)
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh = ev_load['kWh'].sum()
     
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
         
     return(annual_cosumption_kwh,import_cost)

def _get_annual_import_total_kwh(schema):
    
     #get aggregate load
     aggr_load = pd.DataFrame()
     
     #sum ev loads
     for load in get_aggregate_loads(schema):
         aggr_load = load.add(aggr_load, fill_value=0)
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh =aggr_load['kWh'].sum()
     
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
         
     return(annual_cosumption_kwh,import_cost)

def _get_annual_import_with_pv_kwh(schema):           
    
     pv_size,aggr_load = get_optimise_pv_size(schema) 
     
     sum_load = pd.DataFrame()
     
     #sum aggr_load loads
     for load in aggr_load:
         load=pd.DataFrame(load['import_kWh'])
         sum_load = load.add(sum_load, fill_value=0)
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh = sum_load['import_kWh'].sum()
     
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']   
       
     return(annual_cosumption_kwh,import_cost,pv_size)
 
def _get_annual_import_with_pv_and_battery_kwh(schema):
        
        curve,size,results=optimise_battery_size(schema)
        
        cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
        annual_cosumption_kwh = results['P_grid'].sum()
     
        import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
        
        return(size,annual_cosumption_kwh,import_cost)
    

def get_optimise_results(schema):    
    
     #original load
     annual_import_site_kwh,original_import_cost=_get_annual_import_site_kwh(schema)
     
     #EV load
     annual_import_ev_kwh,with_ev_import_cost=_get_annual_import_ev_kwh(schema)
     
     #Total load
     annual_import_total_kwh,cost=_get_annual_import_total_kwh(schema)
     # TODO: Don't call get_ev_loads again
     # TODO: check that inputs are in hour-of-year format
     
     #PV optimised load
     annual_import_with_pv_kwh,cost,pv_size=_get_annual_import_with_pv_kwh(schema)
     
     #PV and battery optimised load
     battery_size,annual_import_with_pv_and_battery_kwh,optimised_import_cost = _get_annual_import_with_pv_and_battery_kwh(schema)
    
     #site results
     
     site = {
            'success': True, 
            'battery_size_kwh': int(battery_size),       
            'annual_import_site_kwh': int(annual_import_site_kwh), 
            'annual_import_ev_kwh': int(annual_import_ev_kwh),   
            'annual_import_total_kwh': int(annual_import_total_kwh),
            'annual_import_with_pv_kwh': int(annual_import_with_pv_kwh),
            'annual_import_with_pv_and_battery_kwh': int(annual_import_with_pv_and_battery_kwh),
            'original_import_cost': int(original_import_cost),
            'with_ev_import_cost': int(with_ev_import_cost), 
            'optimised_import_cost': int(optimised_import_cost)
            }
     
     var = get_variable_fields(schema,fields=['name','num_ev_chargers'])
     
     #building results
     buildings = []
     for name,size,num in zip(var['name'],pv_size,var['num_ev_chargers']):
         buildings.append({'name':name,'pv_size_kw':int(size),'num_of_chargers':num})
         
    
     #building result ditionary set
     
     site = {'site':site}
     
     buildings = {'buildings': buildings}
     
     merge = {**site,** buildings}
     
     results = {'results':merge}
    
     return(json.dumps(results))
     
    
if __name__ == '__main__':
    
    from api_mock import *
    
    #print(get_optimise_results(request.json))
    