import pandas as pd
import datetime
import numpy as np
import csv
import re
import statistics
import dateutil
import os
from datetime import timedelta
try:
    from tkinter.filedialog import askopenfilename
except:
    pass


# import nbimporter
from get_schema import make_schema, time_periodic


def make_df(path, schema):
    s = schema

    df = (
    pd.read_csv(path,
                skiprows=s['skiprows'],
                header=s['header'])
         .drop(columns=s['skipcolumns'])
    )
    
    return df


def num_rpd_periods(df, schema):
    if not schema['file_format'] == 'row_per_day':
        return None
    periods = list(df.drop(columns=[schema['date_column']]).columns)
    try:
        periods = [int(period) for period in periods]
    except:
        return None
    return len(set(periods))


def wide_to_long(df, schema):
    if not schema['file_format'] == 'row_per_day':
        return df, schema
    df = df.melt(id_vars = schema['date_column'],
            var_name = 'time',
            value_name = 'reading')
    try:
        df['time'] = df['time'].astype(int)
    except:
        pass
#     schema['skiprows'] = []
#     schema['skipcolumns'] = []    
    schema['time_column'] = 'time'
    schema['file_format'] = 'single_column'
    schema['time_periodic'] = time_periodic(df, [], 'time')
    return df, schema


def periodic_df(df, schema):
    s = schema
    if not all( [
        s['time_column'],
        s['time_periodic'],
        s['date_column']
    ] ):
        return df, s
    
    period = timedelta(hours=24) / s['time_periodic']
    df[s['time_column']] = df[s['time_column']] * period   
    
    s['time_periodic'] = None
        
    return df, s


def convert_times(df, schema):
    s = schema
    
    if not s['time_column']:
        return df, s
    
    if s['time_periodic']:
        return df, s
    
    try:
        timedelta = (
            pd.to_datetime(df[s['time_column']]) 
            - pd.to_datetime('00:00:00') )

        df[s['time_column']] = timedelta
    except:
        pass
    
    return df, s


def convert_dates(df, schema):
    s = schema
    
    def try_parse_date(col):
        chars = [' ', '-', '_', '/', '#']
        for char in chars:
            dfc = df.copy()
            dfc[col] = dfc[col].str.split(char).str.join(' ')
            try:
                dfc[col] = pd.to_datetime(dfc[col])
                return dfc
            except:
                pass
        return df
        
        
    
    if s['datetime_column']:
        df = try_parse_date(s['datetime_column'])
        
    elif s['date_column'] and s['time_column']:
        df = try_parse_date(s['date_column'])

        df['datetime'] = (
            df[s['date_column']] + df[s['time_column']]
        )
        s['datetime_column'] = 'datetime'
        
    cols_to_drop = []
    if s['date_column']:
        cols_to_drop.append(s['date_column'])
    if s['time_column']:
        cols_to_drop.append(s['time_column'])
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    s['date_column'] = None
    s['time_column'] = None
    df = df.set_index(s['datetime_column'])  
    
    df = df.sort_index()

    return df, s


def sum_phases(df, schema):
    s = schema
    rv = df.sum(axis=1).to_frame(name=s['units'])
    return rv


def apply_schema(path):
    s = make_schema(path)
    df = make_df(path, s)
    df, s = wide_to_long(df, s)
    df, s = periodic_df(df, s)
    df, s = convert_times(df, s)
    df, s = convert_dates(df, s)
    df = sum_phases(df, s)
    return df, s










