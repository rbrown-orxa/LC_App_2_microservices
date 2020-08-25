# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 12:34:28 2020

@author: Sanjeev Kumar
"""

import numpy as np
import pandas as pd
import aggregate_loads as agg
from utils import get_fixed_fields
import matplotlib.pyplot as plt
import logging

def control(P_sun, P_load, E_sto, dt, E_rated):
    """
    P_sun: Generated power from PV (kW)
    P_load: Building load demand (kW)
    E_sto: Energy stored in the battery (kWh)
    dt: Derivate of time step (Hours)
    
    """
    P_nl = P_load - P_sun # Net load -> Power needed by building from grid or battery (or combination)
    # outputs:
    P_sto = 0. # The power flowing into the battery (kW)
    P_grid = 0. # The power imported from the grid (kW)
    P_curt = 0. # The power exported to the grid (kW)
    
    E_next = E_sto - P_nl*dt # Energy stored in the battery at the end of current timestep (kWh)
    
    if P_nl>0: # (load > sun) -> Try to discharge the battery to the building load, if energy is available
        #TODO: Limit rate of discharge of battery
        E_next = E_next if E_next>0. else 0.
        P_sto = (E_next - E_sto)/dt # <0 # Calculate power flowing out of the battery
        P_grid = P_nl + P_sto # Calculate power taken from the grid as load power minus the batter discharge power
    else: # (load <= sun) -> Try to charge the battery
        E_next = E_next if E_next<E_rated else E_rated # Calculate battery charge state. Don't charge if full.
        P_sto = (E_next - E_sto)/dt # >0 # Calculate power flowing into the battery
        P_curt = -P_nl - P_sto#Calculate exported power: difference between net load and power flowing into battery
    return P_sto, P_grid, P_curt


def amortize_batt_cost(cost_per_kwh, life_cycles):
    discharge_cycles_per_day = 1
    days_per_year = 365
    cycles_per_year = discharge_cycles_per_day * days_per_year
    _battery_life_years = life_cycles / cycles_per_year
    _amortized_battery_cost_kwh = cost_per_kwh / _battery_life_years
    return _amortized_battery_cost_kwh


def check_result(E_sto, E_rated, digits=3):
    """Check that battery charge is non-negative and not over capacity"""
    try:
        assert round( E_sto, digits ) >= 0.0, 'Battery charge state is negative'
        assert round ( E_sto, digits ) <= round( E_rated, digits ), 'Battery charge state is greater than capacity'
    except(AssertionError):
        logging.exception(f'E_sto: {E_sto}\tE_rated: {E_rated}')
        raise


def initialise_results_arrays(length, size, intial_charge_percent=50):
    P_sto = np.zeros(length)
    E_sto = np.zeros(length+1)
    P_grid = np.zeros(length)
    P_curt = np.zeros(length)
    E_sto[0]= ( intial_charge_percent / 100 ) * size
    return {'P_sto':P_sto, 'E_sto':E_sto, 'P_grid':P_grid, 'P_curt':P_curt}


def run_control(results, timestep, size, generation, _load, _dt):
    assert isinstance(results, dict)
    for k, v in results.items(): assert isinstance(v, np.ndarray)
        
    results['P_sto'][timestep], results['P_grid'][timestep], results['P_curt'][timestep] = \
        control(generation.values[timestep], _load.values[timestep], results['E_sto'][timestep], dt=_dt, E_rated=size)
    
    results['E_sto'][timestep+1] = results['E_sto'][timestep] + results['P_sto'][timestep] * _dt
    
    check_result( results['E_sto'][timestep+1], size )
    
    return results


def stop_or_continue(cost, prev_cost, keep_iterating):
    
    if prev_cost:
        diff_cost, prev_cost = cost - prev_cost, cost
    else:
        diff_cost, prev_cost = 0, cost
    
    keep_iterating = (keep_iterating+1) if  diff_cost <= 0 else (keep_iterating-1)

    return prev_cost, keep_iterating


def evaluate_results(results, amortized_battery_cost_kwh, batt_size, IMPORT_COST_KWH,
                     _generation, _load, export_price=0.04):
    results['E_sto'] = results['E_sto'][:-1]
    P_pv = _generation - results['P_curt']
    P_nl = _load - _generation

    battery_cost = batt_size * amortized_battery_cost_kwh
    grid_power = results['P_grid'].sum()
    export_power = results['P_curt'].sum()
    import_cost = grid_power * IMPORT_COST_KWH
    export_revenue = export_power * export_price
    total_cost = battery_cost + import_cost - export_revenue
    costs = {'batt_size':batt_size, 'battery_cost':battery_cost,
             'import_cost':import_cost, 'export_revenue':export_revenue,
             'total_cost':total_cost}
    print('.', end='', flush=True)
    return results, costs


def choose_battery_size(performace_data):
    return performace_data.total_cost.idxmin()


def plot_optimisation_curve(performace_data):
    ax = performace_data.plot(subplots=True, grid=True, figsize=(10,5))   

    
def simulate_battery_perfomance(load, generation, batt_cost, import_cost, timestep_hrs, export_price):
    rv = []
    size, prev_cost, keep_iterating = 0, 0, 1
    
    while keep_iterating:

        results = initialise_results_arrays(len(load), size)

        for hour in range(len(load)):
            results = run_control(results, hour, size, generation, load, timestep_hrs)

        results, costs = evaluate_results(results, batt_cost, size, import_cost, generation, load, export_price)
            
        rv.append(costs)
            
        prev_cost, keep_iterating = stop_or_continue( costs['total_cost'], prev_cost, keep_iterating )

        size += 1
    
    return pd.DataFrame(rv).set_index('batt_size')


def get_timestep_in_hours(load_profiles_df):
    try:
        assert load_profiles_df.index.is_all_dates
        freq = load_profiles_df.index.freq
        timestep = freq / pd.tseries.offsets.Hour()
        assert timestep > 0
    except:
        raise TypeError('Unable to determine timestep from load profile data')
    return timestep


def time_index_to_int(dataframe):
    df = dataframe.copy()
    datetimes_df = df.index.to_frame(name='ts').reset_index(drop=True)
    ix = datetimes_df.ts
    week_of_year = ix.dt.week
    day_of_week = ix.dt.dayofweek
    hour_of_day = ix.dt.hour
    hour_of_year = (week_of_year*7*24) + (day_of_week*24) + (hour_of_day)
    df.index = hour_of_year
    return df

def get_gen_load_grid_curt_results(load,generation,size,timestep_hrs):
    results = initialise_results_arrays(len(load), size)
    for hour in range(len(load)):
        results = run_control(results, hour, size, generation, load, timestep_hrs)  
    results={'P_gen':generation,'P_load':np.array(load.values.tolist()),
                 'P_grid':results['P_grid'],'P_curt':-results['P_curt']}
    return(pd.DataFrame(results))

def optimise_battery_size(schema,df,pv_size):
    
    dict = get_fixed_fields(schema,fields=['battery_cost_kwh','battery_life_cycles',
                                           'import_cost_kwh','export_price_kwh'])
    battery_cost_per_kwh = dict['battery_cost_kwh']
    battery_life_cycles=dict['battery_life_cycles']
    import_cost_kwh=dict['import_cost_kwh']
    export_price_kwh=dict['export_price_kwh']
# <<<<<<< HEAD

#     pv_size,df = agg.get_aggregate_loads_site(schema) # seems to call the API needlessly
# =======
# >>>>>>> master
    
    curve = simulate_battery_perfomance(
    load = df['load_kWh'],
    generation = df['gen_kwh'],
    batt_cost = amortize_batt_cost(cost_per_kwh=battery_cost_per_kwh, 
                                   life_cycles=battery_life_cycles), #tesla powerwall
    import_cost = import_cost_kwh,
    timestep_hrs = 1,
    export_price = export_price_kwh)
    
    size = choose_battery_size(curve)
    
    results = get_gen_load_grid_curt_results(load=df['load_kWh'],
                                     generation=df['gen_kwh'],
                                     size=size,
                                     timestep_hrs=1)
    
    return(curve,size,results)


if __name__ == '__main__':
    
    from api_mock import *
    
    print('With Scope factory loads')
    #curve,size,results=optimise_battery_size(request.json)
    #print(curve,size,results)
    #plot_optimisation_curve(curve)


