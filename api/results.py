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
from utils import get_fixed_fields,get_variable_fields,degToCompass
from optimise_pv import get_optimise_pv_size
import config as cfg
import os
from jinja2 import Environment, FileSystemLoader
# import pdfkit
import tempfile
import codecs
import datetime;

def _get_annual_import_site_kwh(schema):
    
     #get base load
     base_load = pd.DataFrame()
     
     #list of consumption
     consumption=[]
     
     #sum base loads
     for load in get_base_loads(schema):
         consumption.append(int(load.sum()[0]))
         base_load = load.add(base_load, fill_value=0)
         
     cost_kwh = get_fixed_fields(schema,fields=['import_cost_kwh'])
     
     annual_cosumption_kwh = base_load['kWh'].sum()
         
     import_cost = annual_cosumption_kwh*cost_kwh['import_cost_kwh']
         
     return(base_load,annual_cosumption_kwh,import_cost,consumption)      
    
         
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
        total_profit, ROI, payback_yrs, install_cost_pv, install_cost, profit_pa)

    

def get_optimise_results(schema):    
    
     #Base load
     (base_load,
        annual_import_site_kwh,
        original_import_cost,consump) = _get_annual_import_site_kwh(schema)
     
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
     dict_report = report(pv_size,battery_size,total_cost,pv_cost,battery_cost,pay_back_yrs_pv,
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
                int(payback_period)
                
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
     
     
     #call html templates build function
     inputs=schema
     
     #update the annual_kwh_consumption_optional value
     for bld,con in zip(inputs['building_data'],consump):
             bld['annual_kwh_consumption_optional']=con
     
     outputs = {'results':merge_results,'charts':merge_charts}
     master_str = build_html_templates(inputs,outputs,dict_report)
     
     # file=codecs.open('./html/master.html',"r")
     # file=file.read()
     # file=str(file)
     
       
     return(json.dumps( {'results':merge_results,'charts':merge_charts,'html':master_str}))
 
    
def report(pv_sz,batt_sz,total_cost,with_pv_cost,with_pv_plus_batt_cost,pay_back_pv,IRR_pv,pay_back_batt,IRR_batt,
           ann_imp_base_kwh,ann_import_pv_kwh,ann_imp_batt_kwh,save_pv,save_batt):
    
    
    dict = {'sys_size_pv':int(sum(pv_sz)),'sys_size_batt':batt_sz,
            'capex_pv':int(with_pv_cost),'capex_batt':int(with_pv_plus_batt_cost),
            'opex_base':int(total_cost),'opex_pv':int(total_cost-save_pv),'opex_batt':int(total_cost-save_batt),
            'payback_yrs_pv':round(pay_back_pv,2),'payback_yrs_batt':round(pay_back_batt,2),
            'irr_pv':round(IRR_pv,2),'irr_batt':round(IRR_batt,2),
            'co2_base':round(ann_imp_base_kwh * cfg.CO2_EMISSION_KWH,2),
            'co2_pv':round(ann_import_pv_kwh * cfg.CO2_EMISSION_KWH,2),
            'co2_batt':round(ann_imp_batt_kwh * cfg.CO2_EMISSION_KWH,0)
            }
   
    return (dict)


def build_html_templates(inputs,outputs,dict_report):
    
    #merge two dictionaries
    dict = {'input':inputs,'output':outputs}
    
    #set template environment
    env = Environment( loader = FileSystemLoader('./templates') )
    
    env.globals.update(zip=zip)
    
    #Site summary
    template = env.get_template('sitesummary.html')
    
    site_summary_str = template.render(data=dict,count=0)
    
    
    #Site Results    
    template = env.get_template('Results.html')
    
    result_str = template.render(data=dict,pv_size=int(dict_report['sys_size_pv']))
    
    #Savings/Economics/Environmental Impact for different modes
    template = env.get_template('report.html')
    
    report_str = template.render(data=dict_report,input=inputs)    
        
    #Battery Cost Curve
    template = env.get_template('line_chart.html')
    
    batt_cost_curve_str = template.render(data=dict,title="Cost vs Battery Size",
                                          name="'" + "cost" + "'")
    
    #Import/Export Yearly
    length=len(dict['output']['charts']['site']['import_export']['Import'])
    dttimelabel =  pd.date_range('2018-12-31', periods=length, freq='60min')   
    dttimelabel = dttimelabel.strftime('%Y-%m-%d %H:%M').to_list()
    
    for row in range(0,len(dttimelabel)):
        dttimelabel[row] = datetime.datetime.strptime(dttimelabel[row],'%Y-%m-%d %H:%M').timestamp()*1000
    
    template = env.get_template('multiline_chart.html')
    
    imp_exp_yr_str = template.render(labels=dttimelabel,
                                 data=dict,
                                 len = 8736,
                                 title="Import/Export",zip=zip)
          
    #Import/Export Weekly    
    template = env.get_template('multiline_chart.html')
    
    imp_exp_wk_str = template.render(labels=dttimelabel[0:24*7],
                                 data=dict,
                                 len=24*7,
                                 title="Sample Week")
    
    #PV Cost Curve    
    template = env.get_template('multi_charts.html')    
  
    pv_cost_curve_str = template.render(data=dict, title="PV Cost Curve",
                                 name="'" + "cost" + "'",
                                 length=len(inputs['building_data']))
    
    #Heat Map    
    template = env.get_template('heat_map.html')
    df = pd.DataFrame(dict['output']['charts']['site']['import_export'])
    df.index = pd.date_range('2018-12-31', periods=len(df), freq='60min')
    df['Month'] = df.index.strftime('%m')
    df['HourOfDay'] = df.index.strftime('%H')
    df = df.groupby(by=['Month','HourOfDay']).mean()
    df = df.reset_index()
    df = df[['Month','HourOfDay','Load']]
    df = df.astype('float')
    df.Month = df.Month - 1
    df.Load = round(df.Load,2)
    values = df.to_numpy()
    
    energy_heat_map_str = template.render(labelx=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                                 labely=list(df.HourOfDay.unique()),
                                 arr = values.tolist(),
                                 title="Energy Consumption Pattern(Load)")
    
        
    #load profile for highest demand day
    df = pd.DataFrame(dict['output']['charts']['site']['import_export'])
    df.index = pd.date_range('2018-12-31', periods=len(df), freq='60min')
    df = df.reset_index()
    df = df.set_index('index',append=True)
    dttime = df.sort_values(by='Load',ascending=False).index[0][1]
    df_max = df.loc[df.index.get_level_values(1).strftime('%Y-%m-%d')==dttime.strftime('%Y-%m-%d')]
     
    
    dttimelabel = df_max.index.get_level_values(1)    
    dttimelabel = dttimelabel.strftime('%Y-%m-%d %H:%M').to_list()    
    for row in range(0,len(dttimelabel)):
        dttimelabel[row] = datetime.datetime.strptime(dttimelabel[row],'%Y-%m-%d %H:%M').timestamp()*1000
    
    template = env.get_template('singleline_chart.html')
    
    load_profile_dmnd_str = template.render(labels=dttimelabel,
                                 data=df_max.Load,
                                 title="Load Profile for highest demand day: " + dttime.strftime('%Y-%m-%d'),zip=zip)
        
    #Master template
    env = Environment( loader = FileSystemLoader('./html') )
    
    template = env.get_template('child_template.html')
    
    #download report file name
    ct=datetime.datetime.now()
    ct=ct.strftime('%Y-%m-%d_%H:%M:%S')
    filename = 'OrxaGrid_LC_App_V2_report_' + ct + '.pdf'
    
    master_str = template.render(
                                site_summary_str=site_summary_str,
                                result_str=result_str,
                                batt_cost_curve_str=batt_cost_curve_str,
                                imp_exp_yr_str=imp_exp_yr_str,
                                imp_exp_wk_str=imp_exp_wk_str,
                                pv_cost_curve_str=pv_cost_curve_str,
                                energy_heat_map_str=energy_heat_map_str,
                                load_profile_dmnd_str=load_profile_dmnd_str,
                                report_str=report_str,
                                length=len(inputs['building_data']), 
                                filename = "'" + filename + "'")
    return(master_str)
    
   
if __name__ == '__main__':
    
    from api_mock import *
    
    #print(get_optimise_results(request.json))
    
