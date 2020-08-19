# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 12:33:24 2020

@author: Sanjeev Kumar
"""


import optimise


### HELPER functions

def _generation_1kw(aggr_load,form_data):
    
    """
    Generation 1Kw based on the aggregated load
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    #Get lat/lon
    lat, lon = float(form_data['lat']), float(form_data['lon'])
    
    #Get list of roof size, roof pitch, azimuth
    roof_size_m2, roofpitch, azimuth = ( form_data['roof_size_m2'].copy(),
                                        form_data['roofpitch'].copy(),
                                        form_data['azimuth'].copy() )
    generation_1kw = [] # list of df
    
    for load, roofpitch, azim in zip(aggr_load, roofpitch, azimuth): 
        tmp_gen = optimise.generation_1kw(lat, lon, load, roofpitch, azimuth=azim)
        generation_1kw.append(tmp_gen) # list of df
        
    return(generation_1kw)


def _optimise_pv_size(generation_1kw,aggr_load,form_data):
    
    """
    optimise PV size based on the aggregated load
    
    generation_1kw: hourly generation in kWh per kWp installed capacity
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    cost_per_kWp = float(form_data['cost_per_kWp'])
    import_cost = float(form_data['import_cost'])
    export_price = float(form_data['export_price'])
    expected_life_yrs = float(form_data['expected_life_yrs'])
    panel_efficiency = 0.18 # https://www.solar.com/learn/solar-panel-efficiency/
    
    roof_size_m2 = form_data['roof_size_m2'].copy()

    optimal_size = []

    # for index in range(num):
    for gen_1_kw, load_kw, roof_size_m2 in zip(
            generation_1kw, aggr_load, roof_size_m2):
        df_cost_curve = optimise.cost_curve(
                                generation_1kw=gen_1_kw,
                                load_kwh=load_kw,
                                cost_per_kWp=cost_per_kWp,
                                import_cost=import_cost,
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                                roof_size_kw=roof_size_m2 * panel_efficiency)

        tmp_opt_size, optimal_revenue = optimise.optimise(df_cost_curve) #float, float        
        optimal_size.append(tmp_opt_size)  
    
    return(optimal_size)