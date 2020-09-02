# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 15:21:28 2020

@author: Sanjeev Kumar
"""

import requests
import json
import pandas as pd
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging
import utils
import datetime as dt
import re

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def generation_1kw(lat=None,lon=None, load=None, 
                    roofpitch=None, start_date='',
                    azimuth=None):
    """
    Get the hourly solar generation timeseries for a grid location, up to one year from start date.
    Return hourly generation in kWh per kWp installed capacity.
    

    
    """
    # utils.call_trace()
#     adjust azimuth for hemisphere
#     adapted from
#     https://github.com/renewables-ninja/gsee >> trigon.py >> line 196
#     azimuth : Deviation of the tilt direction from the meridian.
#     0 = towards pole, going clockwise, 180 = towards equator.
    assert all( [lat, lon, azimuth, roofpitch] )

#Get PV data
    token = '38707fa2a8eb32d983c8fcf348fffd82fe2aa7aa'
    api_base = 'https://www.renewables.ninja/api/'
    s = requests.session()
    s.headers = {'Authorization': 'Token ' + token}
    url = api_base + 'data/pv'
    args = {
        'lat': lat,
        'lon': lon,
        'date_from': '2018-01-01',
        'date_to': '2018-12-31',
        'dataset': 'merra2',
        'capacity': 1.0,
        'system_loss': 0.1,
        'tracking': 0,
        'tilt': roofpitch,
        'azim': azimuth,
        'format': 'json',
        'interpolate': False, 
        'local_time': True
    }
    logging.info(f'Calling API with lat: {lat} and lon: {lon}')
    r = s.get(url, params=args)
    logging.info(f'status code: {r.status_code}')
    parsed_response = json.loads(r.text)
    generation = pd.read_json(
        json.dumps(parsed_response['data']),
        orient='index',
        convert_dates=False)

    old_len = len(generation)

    # generation['local_time'] = generation['local_time'].str.split('+').str[0]
    # generation['local_time'] = generation['local_time'].str.split('-').str[0]
    generation['local_time'] = generation['local_time'].str[:19]

    logging.debug(f"{generation['local_time'].head()}")

    generation['local_time'] = pd.to_datetime(generation['local_time'])

    generation = generation.set_index('local_time')


    logging.debug(f'{generation.head()}')
    logging.debug(f'Index type: {type(generation.index)}')
    logging.debug(f'Index element type: {type(generation.index[0])}')

    # Strip TZ info - only want localtime
    # generation = generation.tz_localize(None) 


    logging.debug(f'generation head: {generation.head()}')
    # Put datetime index into hourly intervals
    start = generation.sort_index().index[0].date()
    end = generation.sort_index().index[-1].date()

    logging.debug(f'start: {start}, end:{end}')

    start = start - dt.timedelta(days=1)
    end = end + dt.timedelta(days=1)
    
    #for index in generation.index:
    #    pd.to_datetime(generation.index)

    logging.debug(f'start: {start}, end:{end}')

    # TODO: check lat/lon valid before calling API
    try: 
        desired_index = pd.date_range(start, end, freq='1H')
    except(ValueError):
        assert False, '422 API datetime error - ' \
                        +'check if lat and lon values are valid'


    
    try:

        generation=    ( generation.reindex(
                            generation.index.union(desired_index))
                            .interpolate()
                            .reindex(desired_index)
                            .dropna() )

    except(ValueError): # Only need this if local time is offset by 30 mins
        pass

    generation = generation[:old_len]

    # Convert index to hour of year
    times = generation.index.to_series()
    generation.index = ( (times.dt.week-1) *7 * 24 
                                 + times.dt.weekday * 24 
                                 + times.dt.hour )
    
    #Sort the index in ascending order
    generation=generation.sort_index()
    
    #remove any duplicated index
    generation=generation[~generation.index.duplicated()]

    logging.debug(f'Length of generation data: {len(generation)}')


    assert len(generation) >= (24*7*52)

    logging.debug(f'{generation.head(10)}')


    return generation[:24*7*52] # clip to same length as building data




def cost_saved_pa(generation_1kw, load_kwh, capacity_kWp, cost_per_kWp, 
                  import_cost, export_price, expected_life_yrs,
                  verbose=False, return_raw_data=False):
    """load must be a dataframe with 1 column,
    naive timestamp index in utc timzone
    and sampled at 1 hour in kWh. 
    Generation input should be hourly in kWh per kWp."""
    import pandas as pd
    load = load_kwh.rename(columns={load_kwh.columns[0]:'load_kWh'})
    if not isinstance(generation_1kw, pd.DataFrame):
        logging.debug(str(type(generation_1kw)))
#         input('Press any key')
    generation_1kw = generation_1kw.rename(columns={
        generation_1kw.columns[0]:'1kWp_generation_kWh'})
    generation = generation_1kw * capacity_kWp
    df = generation.merge(load, 
                            how='inner', 
                            left_index=True, 
                            right_index=True)
    #days = (df.index[-1] - df.index[0]).days
    #confidence = days/365
    df['import_kWh'] = \
        (df['load_kWh'] - df['1kWp_generation_kWh']).clip(lower=0)
    df['export_kWh'] = \
        (df['load_kWh'] - df['1kWp_generation_kWh']).clip(upper=0)
    df = df.rename(columns={
        '1kWp_generation_kWh':
            f'{round(capacity_kWp,2)}_1kWp_generation_kWh'})
    if return_raw_data:
        return df
    df['export_kWh'] = df['export_kWh'].abs()
    
    df = df.sum() # total kWh for the entire year

    old_import_cost = import_cost*(df['load_kWh'])
    new_import_cost = import_cost*(df['import_kWh'])
    
    import_cost_savings = old_import_cost - new_import_cost
    
    export_revenue = export_price * df['export_kWh']
    install_cost = cost_per_kWp * capacity_kWp
    amortized_install_cost = install_cost / expected_life_yrs
    revenue_pa = import_cost_savings + export_revenue
    total_revenue = revenue_pa * expected_life_yrs
    profit_pa = import_cost_savings \
                    + export_revenue \
                    - amortized_install_cost
    total_profit = ( profit_pa * expected_life_yrs )
    
    if verbose:
        ROI = 100 * (total_profit / install_cost)
        payback_yrs = install_cost / revenue_pa
        summary = {'old_import_cost':old_import_cost,
                  'new_import_cost': new_import_cost,
                  'import_cost_savings': import_cost_savings,
                  'export_revenue': export_revenue,
                   'install_cost': install_cost,
                  'amortized_install_cost': amortized_install_cost,
                   'revenue_pa': revenue_pa,
                  'profit_pa': profit_pa,
                   'total_revenue':total_revenue,
                  'total_profit': total_profit,
                  'ROI%': ROI,
                  'payback_yrs': payback_yrs}
        return summary
    return profit_pa


def cost_curve(generation_1kw, load_kwh, cost_per_kWp,
              import_cost, export_price, 
              roof_size_kw, expected_life_yrs):
    
    curve = []
    i = 0
    size_kw=0
    result = cost_saved_pa(generation_1kw, load_kwh,
                                capacity_kWp = size_kw ,
                                cost_per_kWp=cost_per_kWp, 
                                import_cost=import_cost, 
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs)

    
#     while size_kw <= roof_size_kw:
    while result >= 0 and size_kw <= roof_size_kw:
        
        prev_result = result
        result = cost_saved_pa(generation_1kw, load_kwh,
                                capacity_kWp = size_kw ,
                                cost_per_kWp=cost_per_kWp, 
                                import_cost=import_cost, 
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs)
        diff = abs(result - prev_result)
#         print(size_kw, result, diff)
        curve.append((size_kw, result))
        step = 1 / diff if diff > 1 else 1 #adaptive step size
        size_kw += step
        i += 1
    rv = pd.DataFrame(curve, 
        columns=['Size_kWp', 'Profit_PA']).set_index('Size_kWp')
    logging.info(f'PV Optimiser Iterations: {i}')
    return rv

def optimise(cost_curve):
#     cost_curve.plot()
    optimal_size = float(cost_curve.idxmax())
    optimal_revenue = float(cost_curve.max())
#     print(optimal_size, optimal_revenue)
    return optimal_size, optimal_revenue


if __name__ == '__main__':

    FORMAT = '%(asctime)-s\t%(levelname)-s\t%(filename)-s\t' +\
             '%(funcName)-s\tLine:%(lineno)-s\t\t\'%(message)s\''
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)


    gen = generation_1kw(lat=18.520430, lon=73.856743,
                        azimuth=180, roofpitch=30)
    print(gen.head(24))




