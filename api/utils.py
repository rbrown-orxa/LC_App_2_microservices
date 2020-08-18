import os
import functools
import traceback
import pandas as pd


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


def get_consumption_profile(file,consumption_kwh,building_type):
    df = pd.read_csv(file)    
    return(
        df['domestic_kW']*consumption_kwh if building_type == "domestic" else df['non_domestic_kW']*consumption_kwh
            )