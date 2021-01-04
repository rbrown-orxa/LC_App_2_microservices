import pandas as pd
import datetime
import numpy as np
import csv
import re
import statistics
import dateutil
from datetime import timedelta
import warnings
import pytz
from timezonefinder import TimezoneFinder
import datetime as dt
import logging


def columns_to_drop(filepath, skiprows):
    """
    Find columns to drop.
    Return names of columns that are in a known list or with one unique value.
    """
    candidates = ['unit', 'units', 'total', 'totals', 'id']
    df = pd.read_csv(filepath, skiprows=skiprows, sep=None, engine='python')
#     return df
    drop = set()
    
    # find columns according to a list of names we should drop
    for item in df.columns:
        if item.upper() in [x.upper() for x in candidates]:
            drop.add(item)
            
    # find columns with only one unique value
    unique = df.nunique().to_dict()
    for column, n in unique.items():
        if n == 1:
            drop.add(column)
            
    # find columns with int values that are not a time period
    for column in df.columns:
        if df[column].dtype.name == 'int64':
            if df[column].nunique() in [12, 24, 48, 96, 24*60/5, 24*60]:
                continue
            elif df[column].diff().mean().is_integer(): 
                # unlikely for meter reads
                drop.add(column)
                
            # normalise then check that what goes up comes down 
            # true loads should be cyclical
            elif (df[column] / df[column].max()).diff().sum() > 0.5: 
                # unlikely for a load profile
                drop.add(column)

    return list(drop)


def rows_to_skip(filepath):
    """
    Find rows to skip when reading csv file into dataframe.
    Return rows with width less than the mode.
    """
#     print(f'*** Type: {type(filepath)}')
    with open(filepath) as f:
        try:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.reader(f, dialect)
        except:
            f.seek(0)
            reader = csv.reader(f)
        widths = {i: len(row) for i, row in enumerate(reader)}
#         print(widths)
        mode = statistics.mode(widths.values())
        return [row for row, width in widths.items() 
                if width < mode]


def get_format(filepath):
    """
    Determine type of meter data file.
    Return 'row_per_day' or 'single_column'
    """
    with open(filepath) as f:
        try:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.reader(f, dialect)
        except:
            f.seek(0)
            reader = csv.reader(f)
        data = list(reader)
    width = max([len(row) for row in data])
#     print(width)
    
    if width > 20:
        return 'row_per_day'
    else:
        return 'single_column'


def get_units(filepath):
    """
    Find first field containing a unit of power or energy.
    Return 'kw', 'kwh', 'mw', 'mwh', 'w'
    """
    terms = ['kw', 'kwh', 'mw', 'mwh', 'w']
    sub_terms = ['power', ]
    full_patterns = [r'\b' + term + r'\b' for term in terms]
    sub_patterns = [term for term in sub_terms]
    patterns = full_patterns + sub_patterns
    
    converter = {'kw':'kW',
                'kwh':'kWh', 
                'mw':'MW', 
                'mwh':'MWh', 
                'power':'W', 
                'w':'W' }
    
    with open(filepath) as f:
        try:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.reader(f, dialect)
        except:
            f.seek(0)
            reader = csv.reader(f)
        data = list(reader)[:10] # don't look beyond line 10
#         print(data)
    for row in data:
        for word in row:
            found = re.findall(
                r'|'.join(patterns),
                word, 
                flags=re.IGNORECASE)
            if found:
                unique = set(found)
                if not len(unique) > 1:
                    return converter[list(found)[0].lower()]
    return 'W'


def date_column(filepath, skiprows, skipcolumns):
    df = pd.read_csv(filepath, skiprows=skiprows, sep=None, engine='python')
    df = df.drop(columns = skipcolumns)
    df = df.head(10)
    
#     return df

    def try_parse(df):
#         print(df.iloc[1, :])
        # try parsing some rows from each column as date
        for column in df.columns:
            try:
                date = dateutil.parser.parse(df[column].iloc[-1])
                if date.time() == datetime.time(): 
                # time is midnight or time not present / parsed
#                     print('got here')
                    date = dateutil.parser.parse(df[column].iloc[-2]) 
                    # try a different row
                    if date.time() == datetime.time(): 
                    # we have a date column, not datetime column
                        return column
            except:
                continue
        return None
    
    # try without modifying values
    rv = try_parse(df=df)
    if rv:
        return rv
    
    # try modifying values
    chars = ['-', '_', '/', '#']
    for char in chars:
        dfc = df.copy()
        for col in dfc.columns:
            try:
                dfc[col] = dfc[col].str.split(char).str.join(' ')
            except:
                pass # will only work for str type
#         print(char, dfc.iloc[1, :])
        rv = try_parse(df=dfc)
        if rv:
            return rv


def datetime_column(filepath, skiprows, skipcolumns):
    """
    Only a datetime column if date and time present
    """
    df = pd.read_csv(filepath, skiprows=skiprows, sep=None, engine='python')
    df = df.drop(columns = skipcolumns)
#     df = df.head(10)

#     return df

    def try_parse(df):
#         print(df.iloc[1, :])
        # try parsing some rows from each column as date
        head = df.head()
        tail = df.tail()
        for column in df.columns:
            try:
#                 print(dateutil.parser.parse(df[column].iloc[-1]))
                dt_head = dateutil.parser.parse(head[column].iloc[-1])
                dt_tail = dateutil.parser.parse(tail[column].iloc[-1])
#                 print('possible datetime')
#                 if not date.time() == datetime.time():
                if not dt_head.time() == dt_tail.time():
                    if not dt_head.date() == dt_tail.date():
                # time seems to be present (not default parser value)
                        return column
            except:
                continue
        return None
    
    # try without modifying values
    rv = try_parse(df=df)
    if rv:
        return rv
    
    # try modifying values
    chars = ['-', '_', '/', '#']
    for char in chars:
        dfc = df.copy()
        for col in dfc.columns:
            try:
                dfc[col] = dfc[col].str.split(char).str.join(' ')
            except:
                pass # will only work for str type
#         print(char, dfc.iloc[1, :])
        rv = try_parse(df=dfc)
        if rv:
            return rv



def has_header_row(filepath, skiprows=[0]):
    """
    Determine whether first non-skipped row of csv file is a header.
    Return true if header present, otherwise false.
    """
    if skiprows:
        skiprows=max(skiprows)
    else:
        skiprows = 0
    with open(filepath) as f:
        try:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.reader(f, dialect)
        except:
            f.seek(0)
            reader = csv.reader(f)

        data = list(reader)[skiprows:skiprows+10] # don't look beyond line 10
#         print(data)
    
    def isnumber(item):
        try:
            float(item)
            return True
        except:
            return False
        
    first_line = data[0]
    second_line = data[1]
    
    first_line = [isnumber(item) for item in first_line]
    second_line = [isnumber(item) for item in second_line]
    

    if not first_line == second_line:
        return 0
    else:
        return None


def time_column(filepath, skiprows):
    df = pd.read_csv(filepath, skiprows=skiprows, sep=None, engine='python')
    #Fill NA values the previos value
    df=df.ffill(axis=1)
    s = df.nunique()
    hits = s[s.isin([12, 24, 48, 96, 24*60/5, 24*60])]
    if len(hits) == 1:
        return [*hits.to_dict()][0]

    def get_time(val):
        try:
            _time = dateutil.parser.parse(val).time()
            return _time
        except:
            return False
        
    def get_date(val):
        try:
            _time = dateutil.parser.parse(val).date()
            return _time
        except:
            return False
    for name, col in df.iteritems():
        first = get_time(col[0])
        second = get_time(col[1])
#        return col
        if first and first != second: #two different times
#             first = get_date(col[0])
#             second = get_date(col[1])
            first = get_date(col.iloc[1])
            second = get_date(col.iloc[-1])
#             print(first)
#             print(second)
            if first == second: #same dates, i.e. no date parsed
                return name
    return None


def time_periodic(df_or_file, skiprows, time_column):
    if isinstance(df_or_file, pd.core.frame.DataFrame):
        df = df_or_file
    else:
        df = pd.read_csv(
            df_or_file, 
            skiprows=skiprows, 
            sep=None, 
            engine='python')
    
    if time_column and isinstance(df[time_column][0], np.int64):
        return df[time_column].nunique()
    
    return None


def make_schema(path):
    s = {}
    s['skiprows'] = rows_to_skip(path)
    s['skipcolumns'] = columns_to_drop(path, s['skiprows'])
    s['date_column'] = date_column(
        path, s['skiprows'], s['skipcolumns'])
    s['datetime_column'] = datetime_column(
        path, s['skiprows'], s['skipcolumns'])
    s['file_format'] = get_format(path)
    s['units'] = get_units(path)
    s['header'] = has_header_row(path, s['skiprows'])
    s['time_column'] = time_column(path, s['skiprows'])
    s['time_periodic'] = time_periodic(
        path, s['skiprows'], s['time_column'])
    return s


# def test(path):
#     s = {}
#     s['skiprows'] = rows_to_skip(path)
#     print(s)
#     s['skipcolumns'] = columns_to_drop(path, s['skiprows'])
#     print(s)    
#     s['date_column'] = date_column(path, s['skiprows'], s['skipcolumns'])
#     print(s)
#     s['datetime_column'] = datetime_column(path, s['skiprows'], s['skipcolumns'])
#     print(s)
#     s['file_format'] = get_format(path)
#     print(s)
#     s['units'] = get_units(path)
#     print(s)
#     s['header'] = has_header_row(path, s['skiprows'])
#     print(s)
#     s['time_column'] = time_column(path, s['skiprows'])
#     print(s)
#     s['time_periodic'] = time_periodic(path, s['skiprows'], s['time_column'])


def make_df(path, schema):
    s = schema
#     print('***', s['skipcolumns'])

    df = (
    pd.read_csv(path,
                skiprows=s['skiprows'],
                header=s['header'],
                sep=None,
                engine='python')
         
    )
    
#     print(df.head(1))
    df = df.drop(columns=s['skipcolumns'])
    
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
    
    # use different var_name matching date_column is labeled as time
    if schema['date_column'] == 'time':
        df = df.rename(columns = {schema['date_column']:'Date'})
        schema['date_column'] = 'Date'
    
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
#     print(df)
    
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


def is_tz_aware(load):
    return load.index[0].tzinfo is not None


def csv_file_import(path, lat, lon):
    #Read csv, return df with naive local time and electrical unit
    
    df, schema = apply_schema(path)
    units = schema['units']
    logging.info(f'Lat: {lat}, Lon: {lon}')
    
    if is_tz_aware(df):
        df = ( df.tz_localize(None,
                ambiguous='infer',
                nonexistent='shift_forward'))
    return df, units
     


def units_to_kwh(load, units):
    """
    Accept load in a range of units.
    Return load in kWh.
    """
    multiplier = {'kW':10**3, 'kWh':10**3, 'MW':10*6, 'MWh':10**6, 'W':1}
    if not units in multiplier:
        raise KeyError('Could not find units of power or energy')
    load = (load * multiplier[units]) / 10**3 # load now in kW
    logging.warning('Need to fix energy integration when resampling')
 
    return load.rename(columns={units:'kWh'})
    

def resample_hourly(load, units):
    if 'h' not in units:
        return load.resample('1h').mean()
    return load.resample('1h').sum()

def is_utc(load):
    return isinstance(load.index[0].tzinfo, pytz.UTC)

def hour_of_year(load):
    pass

def is_full_year(load):
    return len(load) >= 365 * 24

def pad_missing_hours(load):
    raise NotImplementedError

def pad_missing_days(load):
    raise NotImplementedError


def to_hour_of_year(df):
    """
    Put datetime index into hourly intervals, starting at zero, which
    represents midnight on the Monday closest to 1st January.
    """
    logging.warning('Todo: change start date to first Monday of January')
                  
    #get length, start and end dates
    old_len = len(df)
    start = df.sort_index().index[0].date()
    end = df.sort_index().index[-1].date()
    
    #build desired index, +2d to account for date_range() starting at midnight
    start = start - dt.timedelta(days=1)
    end = end + dt.timedelta(days=1)
    desired_index = pd.date_range(start, end, freq='1H')
    
    #apply new index, interpolate existing values to it. Trim excess rows.
    df=    ( df.reindex(
                df.index.union(desired_index))
                .interpolate()
                .reindex(desired_index)
                .dropna() )
    df = df[:old_len]
    
    # Convert index to hour of year    
    times = df.index.to_series()
    hours = ( (times.dt.week-1) *7 * 24 
                    + times.dt.weekday * 24 
                    + times.dt.hour )
    
    # Get midnight on Monday closest to 1st January, as hour of year
    df['hours'] = hours.values
    midnights = df.between_time('00:00:00', '00:00:00')
    midnights = midnights.reset_index().rename(columns={'index':'timestamp'})
    mondays = midnights [ midnights.timestamp.dt.weekday == 0 ]
    mondays_ascending = mondays.sort_values('hours')
    first_monday_of_year_by_hour = mondays_ascending.hours.min()

    # Shift index so the target Monday mignight is hour zero
    hours_with_first_monday_of_year_as_zero = \
        ( df.hours - first_monday_of_year_by_hour ) % len(df)
    df['hours'] = hours_with_first_monday_of_year_as_zero
    df = df.sort_values('hours')
    df = df.set_index('hours')
    
    return df


def clip_to_year(load):
    return load[:24*7*52]


def process_load_file(path_in, lat, lon):
    df, units = csv_file_import(path_in, lat, lon)
    df = units_to_kwh(df, units)
    df = resample_hourly(df, units)
    assert is_full_year(df)
    df = clip_to_year(df)
    df = to_hour_of_year(df)

    # df.to_csv(path_out)
    return df
    
    
if __name__ == '__main__':
    # path = '../examples/tests/Factory_Heavy_loads_15min.csv'
    path = '../examples/tests/tz_aware_factory_heavy_loads.csv'
    lat, lon = 18.495858, 73.883544 # Pune
    # New York
    # 40.720046, -73.869629
    
    load = process_load_file(path, lat, lon)







