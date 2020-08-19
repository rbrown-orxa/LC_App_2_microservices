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



def generation_1kw(lat=None, lon=None, load=None, roofpitch=None, start_date='', azimuth=None):
    """
    Get the hourly solar generation timeseries for a grid location, up to one year from start date.
    Return hourly generation in kWh per kWp installed capacity.
    

    
    """

#     adjust azimuth for hemisphere
#     adapted from
#     https://github.com/renewables-ninja/gsee >> trigon.py >> line 196
#     azimuth : Deviation of the tilt direction from the meridian.
#     0 = towards pole, going clockwise, 180 = towards equator.
    assert lat is not None
    assert azimuth is not None
#     if lat < 0: # location is in southern hemisphere
#         azimuth = (azimuth + 180) % 360 # rotate 180 deg clockwise and limit to (0, 360)
    
    adjust_year = 0
#     if lat is None:
#         print('Using default latitude of 0.0')
#         lat = 0.0
#     if lon is None:
#         print('Using default longitude of 0.0')
#         lon=0
    assert load is not None or start_date, 'Either load dataframe or start date must be provided'
    if load is not None:
        start = load.sort_index(ascending=True).index[0].date()
    else:
        start = parser.parse(start_date).date()
    latest_end_date = parser.parse('2019-12-31').date()
    end = (start + relativedelta(years=1))
    while end >= latest_end_date:
        print(f'Maximum permissible end date is {latest_end_date}. Date range will be adjusted accordingly')
        end = start
        start = (start - relativedelta(years=1))
        adjust_year += 1
    print('Date range:', start, ' - ',  end)
    token = '38707fa2a8eb32d983c8fcf348fffd82fe2aa7aa'
    api_base = 'https://www.renewables.ninja/api/'
    s = requests.session()
    s.headers = {'Authorization': 'Token ' + token}
    url = api_base + 'data/pv'
    args = {
        'lat': lat,
        'lon': lon,
        'date_from': datetime.strftime(start, format='%Y-%m-%d'),
        'date_to': datetime.strftime(end, format='%Y-%m-%d'),
        'dataset': 'merra2',
        'capacity': 1.0,
        'system_loss': 0.1,
        'tracking': 0,
        'tilt': roofpitch,
        'azim': azimuth,
        'format': 'json',
        'interpolate': False
    }
    print(args)
    r = s.get(url, params=args)
    print (r.status_code)
    print(r.reason)
    assert r.status_code == 200
    parsed_response = json.loads(r.text)
    generation = pd.read_json(json.dumps(parsed_response['data']), orient='index')
    generation = generation.rename(columns={'electricity':'1kWp_generation_kw'})
    if adjust_year: #roll the year of index forward by 1
        generation = generation.reset_index()
        generation['index'] =  generation['index'] + pd.DateOffset(years=adjust_year)
        generation = generation.set_index('index')
    generation = generation.resample('1h').sum() # convert kW to kWh
    metadata = parsed_response['metadata']
    print('Number of days in range: ', (end-start).days)
    print(metadata)
    print(f"Generation for 1 kW: {generation['1kWp_generation_kw'].sum()}")
#     print(generation.head())
    return generation


def cost_saved_pa(generation_1kw, load_kwh, capacity_kWp, cost_per_kWp, 
                  import_cost, export_price, expected_life_yrs,
                  verbose=False, return_raw_data=False):
    """load must be a dataframe with 1 column, naive timestamp index in utc timzone
    and sampled at 1 hour in kWh. Generation input should be hourly in kWh per kWp."""
    import pandas as pd
    load = load_kwh.rename(columns={load_kwh.columns[0]:'load_kWh'})
    if not isinstance(generation_1kw, pd.DataFrame):
        print(type(generation_1kw))
#         input('Press any key')
    generation_1kw = generation_1kw.rename(columns={generation_1kw.columns[0]:'1kWp_generation_kWh'})
    generation = generation_1kw * capacity_kWp
    df = generation.merge(load, how='inner', left_index=True, right_index=True)
    days = (df.index[-1] - df.index[0]).days
    confidence = days/365
    df['import_kWh'] = (df['load_kWh'] - df['1kWp_generation_kWh']).clip(lower=0)
    df['export_kWh'] = (df['load_kWh'] - df['1kWp_generation_kWh']).clip(upper=0)
    df = df.rename(columns={'1kWp_generation_kWh':f'{round(capacity_kWp,2)}_1kWp_generation_kWh'})
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
    profit_pa = import_cost_savings + export_revenue - amortized_install_cost
    total_profit = profit_pa * expected_life_yrs
    
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
    rv = pd.DataFrame(curve, columns=['Size_kWp', 'Profit_PA']).set_index('Size_kWp')
    print('Iterations: ', i)
    return rv

def optimise(cost_curve):
#     cost_curve.plot()
    optimal_size = float(cost_curve.idxmax())
    optimal_revenue = float(cost_curve.max())
#     print(optimal_size, optimal_revenue)
    return optimal_size, optimal_revenue