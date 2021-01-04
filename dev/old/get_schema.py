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



def is_full_year():
    raise NotImplementedError
    # need to know reporting rate
    formats = ['row_per_day', 'single_column']
    df = pd.read_csv(filepath, skiprows=skiprows)
    return df


def columns_to_drop(filepath, skiprows):
    """
    Find columns to drop.
    Return names of columns that are in a known list or with one unique value.
    """
    candidates = ['unit', 'units', 'total', 'totals', 'id']
    df = pd.read_csv(filepath, skiprows=skiprows)
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
            if not df[column].nunique() in [12, 24, 48, 96, 24*60/5, 24*60]:
                drop.add(column)
            
    return list(drop)


def rows_to_skip(filepath):
    """
    Find rows to skip when reading csv file into dataframe.
    Return rows with width less than the mode.
    """
    print(f'*** Type: {type(filepath)}')
    with open(filepath) as f:
        reader = csv.reader(f)
        widths = {i: len(row) for i, row in enumerate(reader)}
        mode = statistics.mode(widths.values())
        return [row for row, width in widths.items() 
                if width < mode]


def get_format(filepath):
    """
    Determine type of meter data file.
    Return 'row_per_day' or 'single_column'
    """
    with open(filepath) as f:
        reader = csv.reader(f)
        data = list(reader)
    width = max([len(row) for row in data])
    
    if width > 20:
        return 'row_per_day'
    else:
        return 'single_column'


def get_units(filepath):
    """
    Find first field containing a unit of power or energy.
    Return 'kw', 'kwh', 'mw', 'mwh', 'w'
    """
    terms = ['kw', 'kwh', 'mw', 'mwh']
    sub_terms = ['power', ]
    full_patterns = [r'\b' + term + r'\b' for term in terms]
    sub_patterns = [term for term in sub_terms]
    patterns = full_patterns + sub_patterns
    
    converter = {'kw':'kW', 'kwh':'kWh', 'mw':'MW', 'mwh':'MWh', 'power':'W'}
    
    with open(filepath) as f:
        reader = csv.reader(f)
        data = list(reader)[:10] # don't look beyond line 10
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
    return 'unknown_units'


def date_column(filepath, skiprows, skipcolumns):
    df = pd.read_csv(filepath, skiprows=skiprows)
    df = df.drop(columns = skipcolumns)
    df = df.head(10)

    def try_parse(df):
#         print(df.iloc[1, :])
        # try parsing some rows from each column as date
        for column in df.columns:
            try:
                date = dateutil.parser.parse(df[column].iloc[-1])
                if date.time() == datetime.time(): # time is midnight or time not present / parsed
                    date = dateutil.parser.parse(df[column].iloc[-2]) # try a different row
                    if date.time() == datetime.time(): # we have a date column, not datetime column
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
    df = pd.read_csv(filepath, skiprows=skiprows)
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
        reader = csv.reader(f)

        data = list(reader)[skiprows:skiprows+10] # don't look beyond line 10
    
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
    df = pd.read_csv(filepath, skiprows=skiprows)
    
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
        if first and first != second: #two different times
            first = get_date(col[0])
            second = get_date(col[1])
            if first == second: #same dates, i.e. no date parsed
                return name
    
    return None


def time_periodic(df_or_file, skiprows, time_column):
    if isinstance(df_or_file, pd.core.frame.DataFrame):
        df = df_or_file
    else:
        df = pd.read_csv(df_or_file, skiprows=skiprows)
    
    if time_column and isinstance(df[time_column][0], np.int64):
        return df[time_column].nunique()
    
    return None


def make_schema(path):
    s = {}
    s['skiprows'] = rows_to_skip(path)
    s['skipcolumns'] = columns_to_drop(path, s['skiprows'])
    s['date_column'] = date_column(path, s['skiprows'], s['skipcolumns'])
    s['datetime_column'] = datetime_column(path, s['skiprows'], s['skipcolumns'])
    s['file_format'] = get_format(path)
    s['units'] = get_units(path)
    s['header'] = has_header_row(path, s['skiprows'])
    s['time_column'] = time_column(path, s['skiprows'])
    s['time_periodic'] = time_periodic(
        path, s['skiprows'], s['time_column'])

    if s['datetime_column'] and s['time_column']:
        s['time_column'] = None # we don't need both, and it causes an error in use_schema.ipynb
    
    return s

