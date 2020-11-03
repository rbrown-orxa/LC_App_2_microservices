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
import config as cfg
import os
from jinja2 import Environment, FileSystemLoader
import pdfkit
import tempfile

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
       
    pv_size, sum_load, df_cost_curve = get_aggregate_loads_site_pv_optimised(schema)
    
    dict = get_fixed_fields(schema, fields=['import_cost_kwh', 'export_price_kwh', 'pv_cost_kwp', 'pv_life_yrs'])
    
    annual_cosumption_kwh = sum_load['import_kWh'].sum()
    
    import_cost = annual_cosumption_kwh * dict['import_cost_kwh']
    
    load_cost = sum_load['load_kWh'].sum() * dict['import_cost_kwh']
    
    import_cost_savings = load_cost - import_cost
    
    export_revenue = sum_load['export_kWh'].abs().sum() * dict['export_price_kwh']
    
    revenue_pa = import_cost_savings + export_revenue
    
    install_cost = dict['pv_cost_kwp'] * sum(pv_size)
    
    amortized_install_cost = install_cost / dict['pv_life_yrs']
    
    profit_pa = import_cost_savings + export_revenue - amortized_install_cost
    
    total_profit = profit_pa * dict['pv_life_yrs']
    
    IRR = 100 * (total_profit / install_cost)
    
    payback_yrs = install_cost / revenue_pa
    
    return (
     annual_cosumption_kwh, import_cost, sum_load, pv_size, df_cost_curve, payback_yrs, IRR, profit_pa)
 
def _get_annual_import_with_pv_and_battery_kwh(schema,df,pv_size):
        
        curve,size,results=optimise_battery_size(schema,df,pv_size)
        
        cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
        annual_cosumption_kwh = results['P_grid'].sum()
     
        import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
        
        return(size,annual_cosumption_kwh,import_cost,curve,results)
    
def _get_lifetimeprofit_roi_payback_period(schema,df,battery_size,pv_size):
    
        discharge_cycles_per_day = 1
        days_per_year = 365
        cycles_per_year = discharge_cycles_per_day * days_per_year
        
        dict = get_fixed_fields(schema,fields=['import_cost_kwh',
                                           'export_price_kwh',
                                           'pv_cost_kwp',
                                           'pv_life_yrs',
                                           'battery_life_cycles',
                                           'battery_cost_kwh'])
        
        old_import_cost = (df['P_load'].sum()) * dict['import_cost_kwh']
        new_import_cost = (df['P_grid'].sum())*dict['import_cost_kwh']
        import_cost_savings = old_import_cost - new_import_cost
        export_revenue = (df['P_curt'].abs().sum()) *  dict['export_price_kwh']
        install_cost_battery = dict['battery_cost_kwh'] * battery_size
        install_cost_pv = dict['pv_cost_kwp']*sum(pv_size)
        install_cost = install_cost_battery + install_cost_pv
        expected_life_yrs_battery = dict['battery_life_cycles']/cycles_per_year
        expected_life_yrs_pv = dict['pv_life_yrs']
        amortized_install_cost_battery = install_cost_battery / expected_life_yrs_battery
        amortized_install_cost_pv = install_cost_pv/expected_life_yrs_pv
        amortized_install_cost =  amortized_install_cost_battery + amortized_install_cost_pv
        revenue_pa = import_cost_savings + export_revenue
        expected_life_yrs = (expected_life_yrs_battery + expected_life_yrs_pv)/2 
        profit_pa = import_cost_savings + export_revenue - amortized_install_cost
        total_profit = profit_pa * expected_life_yrs  
        ROI = 100 * (total_profit / install_cost)
        payback_yrs = install_cost / revenue_pa
        
        return (
        total_profit, ROI, payback_yrs, install_cost_pv, install_cost_battery, profit_pa)

    

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
        pv_size,
        pv_cost_curve,
        pay_back_yrs_pv,
        IRR,savings_pv) = _get_annual_import_with_pv_kwh(schema)
     
     #PV and battery optimised load
     (battery_size,
        annual_import_with_pv_and_battery_kwh,
        battery_optimised_cost,battery_cost_curve,import_export_df) = \
            _get_annual_import_with_pv_and_battery_kwh(
                schema,df,pv_size)
  
    #Get lifetime profit, ROI, payback period in years
     lifetime_profit,ROI,payback_period,pv_cost, battery_cost, savings_batt = \
       _get_lifetimeprofit_roi_payback_period(schema,import_export_df,
                                              battery_size,pv_size)
    #Generate the file report handler 
     handler = report(original_import_cost,pv_cost,battery_cost,pay_back_yrs_pv,
            IRR,payback_period,ROI,annual_import_total_kwh,annual_import_with_pv_kwh,
            annual_import_with_pv_and_battery_kwh,savings_pv,savings_batt
            ) 
    
    
    
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
                int(battery_optimised_cost),
            'lifetime_profit': 
                int(lifetime_profit),
            'roi':
                int(ROI),
            'payback_period':
                int(payback_period),
            'report': handler
                
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
     
     merge_results = {**site,** buildings}
     
     #Generate chart values
     
     #process battery cost curve
     battery_cost_curve=battery_cost_curve.reset_index()
     battery_cost_curve=battery_cost_curve[['batt_size', 'total_cost']]
     
     #process import/export dataframe
     import_export_df.rename(columns = {'P_gen':'Generation',
                                                           'P_load': 'Load',
                                                           'P_grid':'Import',
                                                           'P_curt':'export'}, 
                                                inplace = True)
     
     site = {
             'success': True,
             'battery_cost_curve' :  battery_cost_curve.to_dict(orient='list'),
             'import_export' : import_export_df.to_dict(orient='list')
            }
     
        
     #building results
     buildings = []
     for building_name, curve in zip(var['name'], pv_cost_curve):
         curve = curve.reset_index()
         buildings.append({
             'name':building_name,
             'pv_cost_curve':curve.to_dict(orient='list')
             })
         


     site = {'site':site}
     
     buildings = {'buildings': buildings}
     
     merge_charts = {**site,** buildings}
    
     return(json.dumps( {'results':merge_results,'charts':merge_charts}))
 
    
def report(base_cost,pv_cost,batt_cost,pay_back_pv,IRR_pv,pay_back_batt,IRR_batt,
           ann_imp_base_kwh,ann_import_pv_kwh,ann_imp_batt_kwh,save_pv,save_batt):
    
    df_cost_and_savings = pd.DataFrame({
      'BASE CASE':['', 0, int(base_cost),0,0],
      'WITH PV':['', int(pv_cost), 0,save_pv,''],
      'WITH PV PLUS BATTERY':['', int(batt_cost), 0, '',save_batt]})
    
    df_cost_and_savings.index = ['Cost and savings', 'CAPEX', 'OPEX', 'Annual Savings with PV',
                                 'Annual Savings with PV plus Battery']
    
    df_economics = pd.DataFrame({
      'BASE CASE':['', '', ''],  
      'WITH PV':['', pay_back_pv, IRR_pv],
      'WITH PV PLUS BATTERY':['', pay_back_batt, IRR_batt]})
    
    df_economics.index = ['Economic Metrics', 'payback time', 'IRR']
    
    df_environmental = pd.DataFrame({
      'BASE CASE':['', ann_imp_base_kwh * cfg.CO2_EMISSION_KWH],  
      'WITH PV':['', ann_import_pv_kwh * cfg.CO2_EMISSION_KWH],
      'WITH PV PLUS BATTERY':['', ann_imp_batt_kwh * cfg.CO2_EMISSION_KWH]})
    
    df_environmental.index = ['Environmental Impact', 'CO2 emission metric ton per year']
    
    df = df_cost_and_savings.append(df_economics)
    
    df = df.append(df_environmental)
    
    env = Environment( loader = FileSystemLoader('./templates') )
    
    template = env.get_template('view.html')
    
    filename = os.path.join('./', 'html', 'view.html')
    
    with open(filename, 'w') as fh:
        fh.write(template.render(
           tables=[df.to_html()],titles = ['OrxaGrid Report'])
        )
        
    report = os.path.join('./', cfg.UPLOAD_PATH, 'report.pdf') 
        
    pdfkit.from_file(filename, report)
    
    tf = tempfile.NamedTemporaryFile(dir=cfg.UPLOAD_PATH)
    
    tf.close()
    
    filename = tf.name + '.pdf'
    
    os.rename(report,filename)
    
    return (os.path.basename(filename))

 
     
    
if __name__ == '__main__':
    
    from api_mock import *
    
    #print(get_optimise_results(request.json))
    
