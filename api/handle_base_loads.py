from ingest_file import process_load_file
from utils import get_fixed_fields,get_consumption_profile,get_variable_fields
import os
import config as cfg
import pandas as pd
import logging


def list_buildings(query):
    building_loads = {}
    logging.info('number of buildings: ' + str(len(query['building_data'])) )
    for building in query['building_data']:
        # print('\n', building, end='\n\n')
        if building['load_profile_csv_optional']:
            logging.debug( f"building: {building['name']} refers to a load file:",
                    f" {building['load_profile_csv_optional']} ")
            building_loads[ building['name'] ] = building['load_profile_csv_optional']
        else:
            logging.debug( f"building: {building['name']} needs generic load:" +\
                    f" profile type: {building['building_type']} " +\
                    f" annual consumption in kWh: " +\
                    f"{building['annual_kwh_consumption_optional']}")
            # make a temporary file from get_consumption_profile()
            building_loads[ building['name'] ] = building['annual_kwh_consumption_optional']
            # store it's handle in building_loads
    
    return(building_loads)




def get_base_loads(schema):
    
    #Check total building profile
    dict = get_fixed_fields(schema,fields=['load_profile_csv_optional'])
    handler = dict['load_profile_csv_optional']
    list_of_base_load = []
    
    if not handler:
      
       building_load = list_buildings(schema) # API will be called

       dict = get_variable_fields(schema,fields=['building_type'])
       building_type = dict['building_type']
       for load,btype in zip(building_load.values(),building_type):
           if type(load).__name__=='float' or type(load).__name__=='int':
               #Consumption
               df=get_consumption_profile(cfg.PROFILES_BUILDING,load,btype)
           else:
               #handler
                df = pd.read_csv('./' + cfg.UPLOAD_PATH + '/' + load)
           list_of_base_load.append(df)
    else:
       df = pd.read_csv('./' + cfg.UPLOAD_PATH + '/'+ handler)
       dict = get_variable_fields(schema,fields=['roof_size_m2'])
       roof_sizes_m2 = dict['roof_size_m2']
       list_of_base_load = [roof / sum(roof_sizes_m2) * df for roof in roof_sizes_m2]
    
    return(list_of_base_load)


if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_base_loads(request.json))
