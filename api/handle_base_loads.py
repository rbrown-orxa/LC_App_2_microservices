from ingest_file import process_load_file
from utils import get_fixed_fields,get_consumption_profile,get_variable_fields
import os
import config as cfg
import pandas as pd
import logging
import pycountry_convert as pc
import utils

def list_buildings(query):
    # utils.call_trace()
    building_loads = {}
    logging.info('number of buildings: ' + str(len(query['building_data'])) )
    for building in query['building_data']:
        # print('\n', building, end='\n\n')
        if building['load_profile_csv_optional']:
            building_loads[ building['name'] ] = \
              building['load_profile_csv_optional']
        else:
            # TODO: make a temporary file from get_consumption_profile()
            building_loads[ building['name'] ] = \
              building['annual_kwh_consumption_optional']
            # store it's handle in building_loads
    
    return(building_loads)

def country_to_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
        return country_continent_name
    except:
        assert False, '502 invalid country name'


def get_base_loads(schema):
    
    #Check total building profile
    dict = get_fixed_fields(schema,fields=['load_profile_csv_optional','country'])
    handler = dict['load_profile_csv_optional']
    continent=country_to_continent(dict['country'])
    
    1 if continent in ['Europe','South America','North America','Australia'] else 2
   
    list_of_base_load = []
    
    if not handler:
      
       building_load = list_buildings(schema) # API will be called

       dict = get_variable_fields(schema,fields=['building_type'])
       building_type = dict['building_type'] # domestic,work,public,commercial,delivery
       for load,btype in zip(building_load.values(),building_type):
           if type(load).__name__=='float' or type(load).__name__=='int':
               #Consumption
               profile = 1 if continent in ['Europe','South America','North America','Australia'] else 2
               if profile==1:
                  df=get_consumption_profile(cfg.PROFILES_BUILDING,load,btype)
               else:
                  df=get_consumption_profile(cfg.PROFILES_BUILDING_2,load,btype) 
           else:
               #handler
                df = pd.read_csv('./' + cfg.UPLOAD_PATH + '/' + load)
           list_of_base_load.append(df)
    else:
       df = pd.read_csv('./' + cfg.UPLOAD_PATH + '/'+ handler)
       dict = get_variable_fields(schema,fields=['roof_size_m2'])
       roof_sizes_m2 = dict['roof_size_m2']
       list_of_base_load = [roof / sum(roof_sizes_m2) * df 
                            for roof in roof_sizes_m2]
    
    return(list_of_base_load)


if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_base_loads(request.json))
