#!/usr/bin/env python
# coding: utf-8

# # Load profile 

# In[46]:


import statistics
import werkzeug
import tempfile
import pandas as pd
from contextlib import contextmanager
import os


# In[2]:


#notebook importer
import nbimporter
import pv_optimiser
# import get_schema


# In[ ]:





# # Functions

# In[3]:


def pv_aggregated_load_profile_optimiser(request):
    """
    Get list of optimal pv size for a set of roofs by summing all the load
    profiles, taking the average of variable roof parameters, optimising
    the aggregate system and distributing the suggested solar PV capacity
    across the participant roofs according to the ratios of surface area.
    request: the dict-like request object passed by Flask
    Returns: list of floats
    """    
    fixed_data = _get_fixed_fields(request)
    variable_data = _get_variable_fields(request,
                        average_each_field=True)
    data = {**fixed_data, **variable_data}
    
    #Used as input paramter in EV_profile
    building_type = request.form.get('building_type',type=int)
    no_of_charge_points = request.form.getlist('no_of_charge_points', type=int)

    with _make_temp_files(request) as temp_files:
        curve, df ,report, load = pv_optimiser.api(data, temp_files)

    total_pv_size = report.loc['optimal_size_kwp']
    roof_sizes_m2 = request.form.getlist('roof_size_m2', type=float)
    
    return(_allocate_pv_to_roofs(roof_sizes_m2, total_pv_size,load,building_type,no_of_charge_points))


# In[4]:


def get_form_data(request, fixed_fields=[], variable_fields=[]):
    if fixed_fields:
        fixed_data = _get_fixed_fields(request, fixed_fields) # dict
    else:
        fixed_data = _get_fixed_fields(request)
    if variable_fields:
        variable_data = _get_variable_fields(request, variable_fields) # dict
    else:
        variable_data = _get_variable_fields(request, variable_fields) # dict
    form_data = {**fixed_data, **variable_data} # dict
    return(form_data)


# In[5]:


def pv_allocate_size_by_roof_eff_optimiser(request):
    # fixed_fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price','expected_life_yrs']
    # variable_fields = ['roof_size_m2', 'azimuth', 'roofpitch']

    fixed_data = _get_fixed_fields(request) # dict
    variable_data = _get_variable_fields(request) # dict
    form_data = {**fixed_data, **variable_data} # dict

    lat, lon = float(form_data['lat']), float(form_data['lon'])

    roof_size_m2, roofpitch, azimuth = ( form_data['roof_size_m2'].copy(),
                                        form_data['roofpitch'].copy(),
                                        form_data['azimuth'].copy() )
    #Used as input paramter in EV_profile
    building_type = request.form.get('building_type',type=int)
    no_of_charge_points = request.form.getlist('no_of_charge_points', type=int)
    
    #Initialise dataframe
    load_add = pd.DataFrame()    
    #Get generation per kw   
    generation_1kw = [] # list of df
    generation_1kw_sum = [] # list of float -> annual generation of each roof in kWh

    #Get file names
    # temp_filenames = get_file_names(req,'file')

    with _make_temp_files(request) as temp_files:
        # num = len(temp_files)

        for filepath, roofpitch, azim in zip(temp_files, roofpitch, azimuth):
            load, units = pv_optimiser.csv_file_import(filepath, lat, lon)
            load = pv_optimiser.handle_units(load, units)

            load_add = load.add(load_add, fill_value=0) #DataFrame

            tmp_gen = pv_optimiser.generation_1kw(
                lat, lon, load, roofpitch, azimuth=azim)
            generation_1kw.append(tmp_gen) # list of df
            generation_1kw_sum.append(tmp_gen.sum()) # list of float

        #Calculate roof efficieny
        roof_eff_1kw = []

        roof_eff_1kw = [ roof_generation / (365*24) 
                        for roof_generation in generation_1kw_sum ]


        #allocate the load based on ratio of roof efficiency
        load_kw = []
        tmp_ratio = 0.0
        for roof in roof_eff_1kw: #iterate over each roof
            tmp_df = load_add
            tmp_ratio = roof / sum(roof_eff_1kw) #float
            tmp_df['kWh'] = tmp_df['kWh'] * tmp_ratio['1kWp_generation_kw'] # series  ['1kWp_generation_kw']
            load_kw.append(tmp_df) # list of series -> load for each roof
        #optimise PV size
        cost_per_kWp = float(form_data['cost_per_kWp'])
        import_cost = float(form_data['import_cost'])
        export_price = float(form_data['export_price'])
        expected_life_yrs = float(form_data['expected_life_yrs'])
        panel_efficiency = 0.18 # https://www.solar.com/learn/solar-panel-efficiency/
        optimal_size = []
        
        # for index in range(num):
        for gen_1_kw, load_kw, roof_size_m2 in zip(
                generation_1kw, load_kw, roof_size_m2):
            df_cost_curve = pv_optimiser.cost_curve(
                                    generation_1kw=gen_1_kw,
                                    load_kwh=load_kw,
                                    cost_per_kWp=cost_per_kWp,
                                    import_cost=import_cost,
                                    export_price=export_price,
                                    expected_life_yrs=expected_life_yrs,
                                    roof_size_kw=roof_size_m2 * panel_efficiency)
            
            tmp_opt_size, optimal_revenue = pv_optimiser.optimise(df_cost_curve) #float, float
            optimal_size.append(tmp_opt_size)
    return(optimal_size,[size / sum(optimal_size) * load_kw for size in optimal_size],building_type,no_of_charge_points) # list of float -> optimal size in kWp


# # Helper Functions

# In[6]:


def _get_fixed_fields(request, fields=['lon', 'lat',
                            'cost_per_kWp', 'import_cost',
                            'export_price','expected_life_yrs','no_of_buildings','building_type']):
    """
    Retrieve the constant values from solar pv form.html form fields.
    req: the dict-like request object passed by Flask
    fields: list of the expected keys in req.form
    Returns: Dictionary of {expected form fields:field values}
    """
    return { field : request.form.get(field, None)
            for field in fields }


# In[7]:


def _get_variable_fields(request,
                        fields=['roof_size_m2', 'azimuth',
                                'roofpitch','no_of_charge_points'],
                        average_each_field=False):
    """
    Retrieve the variable values from solar pv form.html form fields.
    req: the dict-like request object passed by Flask
    fields: list of the expected keys in req.form
    Returns: Dictionary of {expected form fields:field values}
    """
    form_data = { field : request.form.getlist(field, type=float)
                 for field in fields }
    if average_each_field:
        form_data = { field : statistics.mean(values)
                    for field, values in form_data.items() }
    return form_data


# In[8]:


@contextmanager
def _make_temp_files(request, key='file'):
    """
    Get list of absolute filepaths of temporary files copied from input files.
    req: the dict-like request object passed by Flask 
        (werkzeug.datastructures.MultiDict of FileStorage)
    key: Form field name of file(s) submitted in HTML
    Returns: list of temporary filepaths
    """
    files = request.files.getlist(key)
    temp_filenames = []
    try:
        for file in files:
            temp_filename = tempfile.mktemp(suffix='.csv')
            # print(f'Temporary file will be created at {temp_filename}')
            # with open(temp_filename, 'wb') as temp_file:
            file.save(temp_filename)
            temp_filenames.append(temp_filename)
        yield temp_filenames
    finally:
        [ os.remove(file) for file in temp_filenames ]


# In[9]:


def _allocate_pv_to_roofs(roof_sizes_m2=[], total_pv_size_kWp=0,load=0,building_type=0,no_of_charge_points=0):
    """Allocate the PV sizes based on ratio of roof sizes"""
    # roof_sizes_m2 = [float(x) for x in roof_sizes_m2]
    return ([roof / sum(roof_sizes_m2) * total_pv_size_kWp for roof in roof_sizes_m2],
            [roof / sum(roof_sizes_m2) * load for roof in roof_sizes_m2],building_type,no_of_charge_points)


# In[ ]:





# In[ ]:





# # Tests

# In[ ]:


if __name__ == '__main__':
    import unittest
    from unittest import TestCase, mock

    class Request:
        pass

    class test_library(TestCase):

        def test__allocate_pv_to_roofs(self):
            rv = _allocate_pv_to_roofs([10, 20, 30], 100+200+300)
            self.assertEqual(rv, [100.0, 200.0, 300.0])

        def test__make_temp_files(self):
            request = Request()
            with open('tempfile1.tmp', 'wb') as f1,                 open('tempfile2.tmp', 'wb') as f2:
                f1.write(b'1,2,3')
                f2.write(b'4,5,6')

            with open('tempfile1.tmp', 'rb') as f1,                 open('tempfile2.tmp', 'rb') as f2:
                    fs1 = werkzeug.datastructures.FileStorage(
                        f1, filename='tempfile1.tmp')
                    fs2 = werkzeug.datastructures.FileStorage(
                        f2, filename='tempfile2.tmp')
                    request.files = werkzeug.datastructures.MultiDict(
                        [('file', fs1), ('file', fs2)])
                    with _make_temp_files(request, 'file') as rv:
                        self.assertIsInstance(rv, list)
                        self.assertEqual(len(rv), 2)

        def test__get_variable_fields(self):
            request = Request()
            request.form = werkzeug.datastructures.MultiDict(
                [('azim', 120), ('azim', 180)])
            fields = ['azim']
            rv = _get_variable_fields(request, fields)
            self.assertEqual(rv['azim'], [120, 180])

            request = Request()
            request.form = werkzeug.datastructures.MultiDict(
                [('azim', 120), ('azim', 180)])
            fields = ['azim']
            rv = _get_variable_fields(request,fields,average_each_field=True)
            self.assertEqual(rv['azim'], 150)

        def test__get_fixed_fields(self):
            request = Request()
            request.form = {'lat':10.0, 'lon':0.0, 'cost':20.0}
            fields = ['lat', 'lon', 'cost', 'missing']
            rv = _get_fixed_fields(request, fields)
            self.assertEqual(rv, 
             {'lat': 10.0, 'lon': 0.0, 'cost': 20.0, 'missing': None})


    unittest.main()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




