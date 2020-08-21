import os
import functools
import traceback
import pandas as pd
import config as cfg
import optimise

def handle_exceptions(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                # print(traceback.format_exc(err))
                return handle(err)
        def handle(err):
            msg = str(err).split('\n')[0]
            code = msg.split()[0]
            if code.isnumeric():
                return ( {'error':msg}, code )
            return ( {'error':msg}, 500 )
        return wrapper


def init_file_handler(upload_path):
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)


def _schema():
    with open('my-schema.json') as file:
        schema = file.read()
    return schema


def _result_schema():
    with open('result-schema.json') as file:
        schema = file.read()
    return schema

<<<<<<< HEAD
def get_fixed_fields(schema, fields=['lon', 'lat', 'cost_per_kWp', 
                                       'import_cost_kwh','export_price_kwh',
                                       'pv_cost_kwp', 'pv_life_yrs', 
                                       'battery_life_cycles', 'battery_cost_kwh',
                                       'load_profile_csv_optional']):
    """
    Retrieve the constant values from LC app form fields.
    req: the dict-like request object passed by Flask
    fields: list of the expected keys in req.form
    Returns: Dictionary of {expected form fields:field values}
    """
    return ( {field : schema.get(field, None) for field in fields} )

def get_form_data(schema,fixed_fields,variable_fields):
    
    fixed_data = get_fixed_fields(schema,fixed_fields)
    
    variable_data = get_variable_fields(schema,variable_fields)

    return({**fixed_data,**variable_data})


def get_variable_fields(schema,fields=['roof_size_m2', 'azimuth_deg','pitch_deg']):
    """
    Retrieve the variable values form fields.
    req: the dict-like request object passed by Flask
    fields: list of the expected keys in req.form
    Returns: Dictionary of {expected form fields:field values}
    """
    building_data=schema.get('building_data')
    super_dict = {}
    for d in building_data:
        for k, v in d.items():
            super_dict.setdefault(k, []).append(v)
    return ( {field : super_dict.get(field, None) for field in fields} )

=======
>>>>>>> 3a66c48bf832a3da065cffda53de1966c82deace

def get_consumption_profile(file,consumption_kwh,building_type):
    
    if building_type == "domestic":
        df = pd.read_csv(file, header=0,usecols=['domestic_kW'])
        df = df*consumption_kwh
        df.rename(columns={'domestic_kW':'kWh'},inplace=True)
    else:
        df = pd.read_csv(file, header=0,usecols=['non_domestic_kW'])
        df = df*consumption_kwh
        df.rename(columns={'non_domestic_kW':'kWh'},inplace=True)
   
    df.index.name='hours'
    
    return(df)

def get_generation_1kw(form_data):
    
    """
    Generation 1Kw based on the aggregated load
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    #Get lat/lon
    lat, lon = float(form_data['lat']), float(form_data['lon'])
    
    start_date = '2018-12-31'
    
    #Get list of roof size, roof pitch, azimuth
    roofpitch, azimuth = ( form_data['pitch_deg'].copy(),form_data['azimuth_deg'].copy() )
    generation_1kw = [] # list of df
    
    for pitch, azim in zip(roofpitch, azimuth): 
        tmp_gen = optimise.generation_1kw(lat=lat, lon=lon,start_date=start_date,
                                          roofpitch=pitch, azimuth=azimuth)
        generation_1kw.append(tmp_gen)
        
    return(generation_1kw)



def optimise_pv_size(generation_1kw,aggr_load,form_data):
    
    """
    optimise PV size based on the aggregated load
    
    generation_1kw: hourly generation in kWh per kWp installed capacity
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    cost_per_kWp = float(form_data['pv_cost_kwp'])
    import_cost = float(form_data['import_cost_kwh'])
    export_price = float(form_data['export_price_kwh'])
    expected_life_yrs = float(form_data['pv_life_yrs'])
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



if __name__ == '__main__':
    
    from api_mock import *
    
    fixed_fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost_kwh', 
              'export_price_kwh','pv_cost_kwp', 'pv_life_yrs', 
              'battery_life_cycles', 'battery_cost_kwh',
                   'load_profile_csv_optional']
    
    variable_fields = ['roof_size_m2', 'azimuth_deg','pitch_deg']
      
    print(get_form_data(request.json,fixed_fields,variable_fields))
        
    print(get_consumption_profile(cfg.PROFILES_BUILDING,1000,'domestic'))