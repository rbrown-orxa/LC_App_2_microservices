<<<<<<< HEAD
from ingest_file import process_load_file
from utils import get_fixed_fields,get_consumption_profile,get_variable_fields
import os
import config as cfg
=======

>>>>>>> 3a66c48bf832a3da065cffda53de1966c82deace

def list_buildings(query):
    building_loads = {}
    print(type(query))
    print('number of buildings: ',  len(query['building_data']) )
    for building in query['building_data']:
        # print('\n', building, end='\n\n')
        if building['load_profile_csv_optional']:
            print( f"building: {building['name']} refers to a load file:",
                    f" {building['load_profile_csv_optional']} ")
            building_loads[ building['name'] ] = building['load_profile_csv_optional']
        else:
            print( f"building: {building['name']} needs generic load:",
                    f" profile type: {building['building_type']} ",
                    f" annual consumption in kWh: "
                    f"{building['annual_kwh_consumption_optional']}")
            # make a temporary file from get_consumption_profile()
<<<<<<< HEAD
            building_loads[ building['name'] ] = building['annual_kwh_consumption_optional']
            # store it's handle in building_loads
    return building_loads




def get_base_loads(schema):
    
    #Check total building profile
    dict = get_fixed_fields(schema,fields=['load_profile_csv_optional','lat','lon'])
    lat = dict['lat']
    lon = dict['lon']
    raw_path = dict['load_profile_csv_optional']
    list_of_base_load = []
    
    if not raw_path:
       building_load = list_buildings(schema)
       dict = get_variable_fields(schema,fields=['building_type'])
       building_type = dict['building_type']
       for load,btype in zip(building_load.values(),building_type):
           if type(load).__name__=='float':
               df=get_consumption_profile(cfg.PROFILES_BUILDING,load,btype)
           else:
               if os.path.isfile(load):
                   df = process_load_file(path_in=load, lat=lat, lon=lon)
           list_of_base_load.append(df)
    else:
       df = process_load_file(path_in=raw_path, lat=lat, lon=lon)
       dict = get_variable_fields(schema,fields=['roof_size_m2'])
       roof_sizes_m2 = dict['roof_size_m2']
       list_of_base_load = [roof / sum(roof_sizes_m2) * df for roof in roof_sizes_m2]
    
    return(list_of_base_load)
    
    




if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_base_loads(request.json))
=======

            # store it's handle in building_loads
    return building_loads

>>>>>>> 3a66c48bf832a3da065cffda53de1966c82deace
