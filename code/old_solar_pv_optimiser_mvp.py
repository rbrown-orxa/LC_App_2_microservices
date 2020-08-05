#!/usr/bin/env python
# coding: utf-8

# # Algorithm for optimal sizing of a Solar PV plant to maximise annual profit

# # TODO:

# #### DONE - Get start date from raw data and pass into generation prediction
# #### DONE - Use floating point range for optimisation iterator
# #### DONE - Coerce prediction range to a previous year if that maxmimises the days of prediction (aim for 365)
# #### DONE - Find the optimal value of kWp
# #### DONE - Calculate range for iteration of cost_pa curve from load profile or implement hill climbing algorithm
# #### Web dashboard for user to input parameters and upload load file

# # User Data Entry

# In[1]:


# load_data_path = 'Factory_Heavy_loads_15min.csv'
# lat = 18.640976
# lon = 73.833332
# cost_per_kWp=1840
# import_cost=0.14
# export_price=0.04
# expected_life_yrs=20
# roof_size_kw=100
# Assume south facing with 35 deg tilt angle


# # Imports

# In[2]:


import pandas as pd
import requests
import json
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime
import matplotlib.pyplot as plt
import json
import matplotlib


# import warnings
# warnings.simplefilter('error', RuntimeWarning)

# In[3]:


# get_ipython().run_line_magic('matplotlib', 'inline')


# # Functions

# In[4]:


def orxa_PDS_import(path):
    """Format must be same as Factory_Heavy_loads_15min.csv"""
    df = pd.read_csv(path, parse_dates=['ReportedDateTime',])
    df['ReportedDateTime'] = pd.to_datetime(df['ReportedDateTime'], format='%Y-%m-%d_%H:%M:%S')
    df = df.set_index('ReportedDateTime')
    df = df.drop(columns=['ProductDataStreamId'])
    df = (df.sum(axis=1).to_frame(name='load_kw')) / 1000 #convert W to kW
    df = (df.tz_localize('Asia/Kolkata') #add IST offset
                .tz_convert('UTC') #convert to UTC offset
                .tz_localize(None) #remove offset
                .resample('1h')
                .mean())
    return df


# In[5]:


#Scope factory coordinates: 18.640976, 73.833332
def generation_1kw(lat=None, lon=None, load=None, start_date=''):
    """Get the hourly solar generation timeseries for a grid location, up to one year from start date"""

    adjust_year = False
    if lat is None:
        print('Using default latitude of 0.0')
        lat = 0.0
    if lon is None:
        print('Using default longitude of 0.0')
        lon=0
    assert load is not None or start_date, 'Either load dataframe or start date must be provided'
    if load is not None:
        start = load.sort_index(ascending=True).index[0].date()
    else:
        start = parser.parse(start_date).date()
    latest_end_date = parser.parse('2019-12-31').date()
    end = (start + relativedelta(years=1))
    if end >= latest_end_date:
        print(f'Maximum permissible end date is {latest_end_date}. Date range will be adjusted accordingly')
        end = start
        start = (start - relativedelta(years=1))
        adjust_year = True
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
        'tilt': 35,
        'azim': 180,
        'format': 'json'
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
        generation['index'] =  generation['index'] + pd.DateOffset(years=1)
        generation = generation.set_index('index')
    metadata = parsed_response['metadata']
    print('Number of days in range: ', (end-start).days)
    print(metadata)
    return generation


# In[6]:


def cost_saved_pa(generation_1kw, load, capacity_kWp, cost_per_kWp, 
                  import_cost, export_price, expected_life_yrs,
                  verbose=False, return_raw_data=False):
    """load must be a dataframe with 1 column, naive timestamp index in utc timzone
    and sampled at 1 hour."""
    import pandas as pd
    load = load.rename(columns={load.columns[0]:'load_kw'})
    if not isinstance(generation_1kw, pd.DataFrame):
        print(type(generation_1kw))
        input('Press any key')
    generation_1kw = generation_1kw.rename(columns={generation_1kw.columns[0]:'1kWp_generation_kw'})
    generation = generation_1kw * capacity_kWp
    df = generation.merge(load, how='inner', left_index=True, right_index=True)
    days = (df.index[-1] - df.index[0]).days
    confidence = days/365
    df['import_kw'] = (df['load_kw'] - df['1kWp_generation_kw']).clip(lower=0)
    df['export_kw'] = (df['load_kw'] - df['1kWp_generation_kw']).clip(upper=0)
    df = df.rename(columns={'1kWp_generation_kw':f'{round(capacity_kWp,2)}_kWp_generation_kw'})
    if return_raw_data:
        return df
    df['export_kw'] = df['export_kw'].abs()
    kwh = df.sum() #timebase is in hours, so result is in kwh
    old_import_cost = import_cost*(kwh['load_kw'])
    new_import_cost = import_cost*(kwh['import_kw'])
    import_cost_savings = old_import_cost - new_import_cost
    export_revenue = export_price * kwh['export_kw']
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


# In[7]:


def cost_curve(generation_1kw, load, cost_per_kWp,
              import_cost, export_price, 
              roof_size_kw, expected_life_yrs):
    
    curve = []
    i = 0
    size_kw=0
    result = cost_saved_pa(generation_1kw, load,
                                capacity_kWp = size_kw ,
                                cost_per_kWp=cost_per_kWp, 
                                import_cost=import_cost, 
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs)
    
    while result >= 0 and size_kw <= roof_size_kw:
        prev_result = result
        result = cost_saved_pa(generation_1kw, load,
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


# In[8]:


def optimise(cost_curve):
#     cost_curve.plot()
    optimal_size = float(cost_curve.idxmax())
    optimal_revenue = float(cost_curve.max())
#     print(optimal_size, optimal_revenue)
    return optimal_size, optimal_revenue


# In[9]:


def plot_curve(cost_curve, optimal_size, optimal_revenue):
#     cost_curve.plot(figsize=(15,3))
    fig, ax = plt.subplots(figsize=(15,3))
    df_cost_curve.plot(ax=ax)
    plt.plot([optimal_size,optimal_size],[0,optimal_revenue],'k--', linestyle = ":", lw=1) #[startx, endx],[starty, endy]
    plt.plot([cost_curve.index[-1],0],[optimal_revenue,optimal_revenue],'k-', linestyle = ":", lw=1) #[startx, endx],[starty, endy]
    plt.show()


# In[10]:


def generate_report(generation, load, size, cost_per_kWp, import_cost,
                    export_price, expected_life_yrs):
    summary = {'optimal_size_kwp': size}
    summary.update(cost_saved_pa(generation, load,
                                capacity_kWp = size,
                                cost_per_kWp=cost_per_kWp, 
                                import_cost=import_cost, 
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs, 
                                verbose=True))
    
    
    df = pd.DataFrame.from_dict(summary, orient='index', columns=['Value'])
#     js = df.to_json()
    return df


# In[11]:


def plot_loads(generation, load, size):
    df = cost_saved_pa(generation, load,
                                capacity_kWp = size,
                                cost_per_kWp=cost_per_kWp, 
                                import_cost=import_cost, 
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                      return_raw_data=True)#['20190401':'20190407']
#     df.plot(figsize=(15,15), subplots=True)
    df.plot(figsize=(15,5))





def api(dict_input, file):
    # dict_input = json.loads(json_input)

    assert file is not None
    for k, v in dict_input.items():
        assert v is not None

    lat = float(dict_input['lat'])
    lon = float(dict_input['lon'])
    cost_per_kWp= float(dict_input['cost_per_kWp'])
    import_cost=float(dict_input['import_cost'])
    export_price=float(dict_input['export_price'])
    expected_life_yrs=float(dict_input['expected_life_yrs'])
    roof_size_kw=float(dict_input['roof_size_kw'])


    load = orxa_PDS_import(file)
    generation = generation_1kw(lat=lat, lon=lon, load=load)
    df_cost_curve = cost_curve(generation_1kw=generation,
                                load=load,
                                cost_per_kWp=cost_per_kWp,
                                import_cost=import_cost,
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                                roof_size_kw=roof_size_kw)

    optimal_size, optimal_revenue = optimise(df_cost_curve)
    report = generate_report(generation, load, optimal_size, cost_per_kWp, 
                    import_cost, export_price, expected_life_yrs)
    report_dict = report.to_dict()
    curve_dict = df_cost_curve.to_dict()

    df = cost_saved_pa(generation, load,
                                capacity_kWp = optimal_size,
                                cost_per_kWp=cost_per_kWp, 
                                import_cost=import_cost, 
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                      return_raw_data=True)#['20190401':'20190407']
#     df.plot(figsize=(15,15), subplots=True)


    report_dict['cost_curve'] = curve_dict['Profit_PA']
    # plot = df_cost_curve.plot()
    # return json.dumps(report_dict['Value'], indent=4)
    return df_cost_curve, df, report.to_html()
    return report.to_html()
    return report_dict
    return json.dumps(report_dict, indent=4)


# # Script

# In[12]:

if __name__ == '__main__':

    load = orxa_PDS_import(load_data_path)
    # load.plot()


    # In[13]:


    generation = generation_1kw(lat=lat, lon=lon, load=load)
    # generation.plot()


    # In[14]:


    df_cost_curve = cost_curve(generation_1kw=generation,
                                load=load,
                                cost_per_kWp=cost_per_kWp,
                                import_cost=import_cost,
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                                roof_size_kw=roof_size_kw)
    # df_cost_curve.plot()


    # In[15]:


    optimal_size, optimal_revenue = optimise(df_cost_curve)


    # In[16]:


    plot_curve(df_cost_curve, optimal_size, optimal_revenue)


    # In[17]:


    report = generate_report(generation, load, optimal_size)
    report


    # In[18]:


    generation.plot()


    # In[19]:


    load.plot()


    # In[20]:


    plot_loads(generation, load, optimal_size)


    # In[ ]:




