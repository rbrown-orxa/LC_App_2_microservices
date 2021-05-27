from ingest_file import process_load_file
from utils import get_fixed_fields,get_consumption_profile,get_variable_fields
import os
import config as cfg
import pandas as pd
import logging
from minio import Minio
from minio.error import S3Error
from io import BytesIO, StringIO

import utils


MINIO_CONN_STR = cfg.MINIO_CONN_STR
MINIO_USER = cfg.MINIO_USER
MINIO_PW = cfg.MINIO_PW
MINIO_SECURE = cfg.MINIO_SECURE
MINIO_RAW_BUCKET = cfg.MINIO_RAW_BUCKET
MINIO_CLEANED_BUCKET = cfg.MINIO_CLEANED_BUCKET



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




def get_base_loads(schema):

    print(f'MINIO_CONN_STR: {MINIO_CONN_STR}')
    print(f'MINIO_SECURE: {MINIO_SECURE}')


    #Check total building profile
    _dict = get_fixed_fields(schema,fields=['load_profile_csv_optional'])
    handler = _dict['load_profile_csv_optional']
    list_of_base_load = []
    
    if not handler:
      
      building_load = list_buildings(schema) # API will be called

      _dict = get_variable_fields(schema,fields=['building_type'])
      building_type = _dict['building_type'] # domestic,work,public,commercial,delivery
      for load,btype in zip(building_load.values(),building_type):
        if type(load).__name__=='float' or type(load).__name__=='int':
          #Consumption
          df=get_consumption_profile(cfg.PROFILES_BUILDING,load,btype)
          # breakpoint()
        else:
           #handler

          # Read pre-processed file from bucket into DataFrame
          client = Minio(MINIO_CONN_STR, MINIO_USER, MINIO_PW, secure=MINIO_SECURE)
          raw_file = client.get_object(MINIO_CLEANED_BUCKET, load)
          raw_buf_b = BytesIO(raw_file.read())
          #TODO: Get encoding for use in decode() function below
          raw_buf_t = StringIO(raw_buf_b.read().decode())
          df = pd.read_csv(raw_buf_t)
        list_of_base_load.append(df)
    
    else:
      # Read pre-processed file from bucket into DataFrame
      client = Minio(MINIO_CONN_STR, MINIO_USER, MINIO_PW, secure=MINIO_SECURE)
      raw_file = client.get_object(MINIO_CLEANED_BUCKET, handler)
      raw_buf_b = BytesIO(raw_file.read())
      #TODO: Get encoding for use in decode() function below
      raw_buf_t = StringIO(raw_buf_b.read().decode())
      df = pd.read_csv(raw_buf_t)

      _dict = get_variable_fields(schema,fields=['roof_size_m2'])
      roof_sizes_m2 = _dict['roof_size_m2']
      list_of_base_load = [roof / sum(roof_sizes_m2) * df 
                          for roof in roof_sizes_m2]
    
    return(list_of_base_load)


if __name__ == '__main__':
    
    from api_mock import *
    
    print(get_base_loads(request.json))



