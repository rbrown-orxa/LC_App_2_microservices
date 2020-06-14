from flask import Flask, request, url_for, send_file, Markup
from flask import Flask, flash, redirect, render_template, request, session, abort,url_for,send_file, Markup
import matplotlib
from io import BytesIO, StringIO
import io
import os
import tempfile
from flask import render_template
import nbimporter
import pandas as pd

import plotting
import pv_optimiser

matplotlib.use('Agg')
app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('form.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return render_template('form.html')
    else:
        flash('wrong password!')
        return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
	
	
@app.route("/help")
def help():
    return render_template('help.html')
	
@app.route("/PrivacyPolicy")
def PrivacyPolicy():
    return render_template('PrivacyPolicy.html')
	
    
def get_fixed_form_fields(req,fields):
    #Get fields
    form_data = {}
    for field in fields:
        form_data[field] = req.form.get(field, None)
    return(form_data)
        
def get_var_form_fields(req,fields,avg=0):
    
    form_data = {}
    for field in fields:
        vars = []
        if req.form.getlist(field):
            if avg > 0:
                vars = req.form.getlist(field)
                tmp = 0.0
                for var in vars:
                    tmp = tmp + float(var)
                form_data[field] = tmp / len(vars)
            else:                
                form_data[field] = req.form.getlist(field)
    return(form_data)

def get_file_names(req,key):
    #Get file list
    files = req.files.getlist(key)
    temp_filenames = []
    for file in files:
        temp_filename = tempfile.mktemp(suffix='.csv')
        print(f'Temporary file will be created at {temp_filename}')
        with open(temp_filename, 'wb') as temp_file:
            file.save(temp_file)
            temp_filenames.append(temp_filename)
    return(temp_filenames)
    
def pv_allocate_size_by_roof_eff_optimiser(req):
    fixed_fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price','expected_life_yrs']
    variable_fields = ['roof_size_m2', 'azimuth', 'roofpitch']
    
    #Get fixed form fields
    form_data = get_fixed_form_fields(req,fixed_fields)
    #Get variable form fields
    form_data.update(get_var_form_fields(req,variable_fields,0))
    #Get file names
    temp_filenames = get_file_names(req,'file')
    print(form_data)
    
    #Get lat/lon
    lat = float(form_data['lat'])
    lon = float(form_data['lon'])
    #Get roof size
    roof_size_m2 = []
    vars = form_data['roof_size_m2']
    for var in vars:
        roof_size_m2.append(float(var))
    #Get roof pitch
    roofpitch = []
    vars = form_data['roofpitch']
    for var in vars:
        roofpitch.append(float(var))
    #Get azimuth
    azimuth = []
    vars = form_data['azimuth']
    for var in vars:
        azimuth.append(float(var))
    #Initialise dataframe
    load_add = pd.DataFrame()    
    #Get generation per kw   
    generation_1kw = []
    generation_1kw_sum = []
    #No of buildings
    num = len(temp_filenames)
    for index in range(num):
        load, units = pv_optimiser.csv_file_import(temp_filenames[index], lat, lon)
        load = pv_optimiser.handle_units(load, units)
        load_add = load.add(load_add, fill_value=0)
        tmp_gen = pv_optimiser.generation_1kw(lat=lat, lon=lon, roofpitch=roofpitch[index], load=load, azimuth=azimuth[index])
        generation_1kw.append(tmp_gen)
        generation_1kw_sum.append(tmp_gen.sum())
    #Calculate roof efficieny
    roof_eff_1kw = []
    tmp_df = load_add
    for index in range(num):
        roof_eff_1kw.append(generation_1kw_sum[index]/(365*24))
    #allocate the load based on ratio of roof efficiency
    load_kw = []
    tmp_ratio = 0.0
    for index in range(num):
        tmp_df = load_add
        tmp_ratio = roof_eff_1kw[index]/sum(roof_eff_1kw)
        tmp_df['kWh'] = tmp_df['kWh'] * tmp_ratio['1kWp_generation_kw']
        load_kw.append(tmp_df)
    #optimise PV size
    cost_per_kWp = float(form_data['cost_per_kWp'])
    import_cost = float(form_data['import_cost'])
    export_price = float(form_data['export_price'])
    expected_life_yrs = float(form_data['expected_life_yrs'])
    panel_efficiency = 0.18 # https://www.solar.com/learn/solar-panel-efficiency/
    optimal_size = []
    for index in range(num):
        df_cost_curve = pv_optimiser.cost_curve(generation_1kw=generation_1kw[index],
                                load_kwh=load_kw[index],
                                cost_per_kWp=cost_per_kWp,
                                import_cost=import_cost,
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                                roof_size_kw=roof_size_m2[index] * panel_efficiency)
        tmp_opt_size, optimal_revenue = pv_optimiser.optimise(df_cost_curve)
        optimal_size.append(tmp_opt_size)
        
    #remove temporary files
    for file in temp_filenames:
            os.remove(file)
            print(f'Temporary file removed: {file}')    
    
    return(optimal_size)
    
    
    
def pv_aggregated_load_profile_optimiser(req):
    
    fields = ['no_of_buildings','lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price',
                    'expected_life_yrs', 'roof_size_m2', 'azimuth', 'roofpitch']
    
    fixed_fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price','expected_life_yrs']
    variable_fields = ['roof_size_m2', 'azimuth', 'roofpitch']
    
    #Get fixed form fields
    form_data = get_fixed_form_fields(req,fixed_fields)
    #Get variable form fields with Average
    form_data.update(get_var_form_fields(req,variable_fields,1))
    #Get file names
    temp_filenames = get_file_names(req,'file')
    
    #Call PV optimiser using aggegated load
    curve, loads, report = pv_optimiser.api(form_data, temp_filenames)
    
    #Get optimal PV size
    total_pv_size = report.loc['optimal_size_kwp']
    
    #Get roof size
    roof_size = []
    sizes = req.form.getlist('roof_size_m2')
    for size in sizes:
        roof_size.append(size)
        
    #Convert into float
    roof_size =  [float(x) for x in roof_size]
    
    #allocate the PV size based on ratio of roof size
    optimal_size = []
    for roof in roof_size:
        optimal_size.append((roof/sum(roof_size))*total_pv_size)
    
    #remove temporary files
    for file in temp_filenames:
            os.remove(file)
            print(f'Temporary file removed: {file}')
    
    return(optimal_size)  
    

@app.route("/submit", methods=["POST"])
def get_data():
    if False:#not session.get('logged_in'):
        return render_template('login.html')
    else:
        
        #fields = ['no_of_buildings','lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price',
        #            'expected_life_yrs', 'roof_size_m2', 'azimuth', 'roofpitch']
        
        #Call allocate pv size by roof efficiency function
        #print("Allocate PV size based on roof efficiency")
        #optimal_size = pv_allocate_size_by_roof_eff_optimiser(request)
        
        #Call aggregated load profile function
        print("Allocate PV size based on aggregated load profile based on average roof paramters")
        optimal_size = pv_aggregated_load_profile_optimiser(request)
        print(optimal_size)
        
        #if 'debug_api' in request.form:
        #    return(form_data)
        
        #curve, loads, report = pv_optimiser.api(form_data, temp_filenames)
       
        #for file in temp_filenames:
        #    os.remove(file)
        #    print(f'Temporary file removed: {file}')

        #sample_week = plotting.get_plot(
        #    loads.iloc[:24*7,:], size=(10,2), title='Sample Week')
        #curve = plotting.get_plot(curve, size=(5,3), title='Optimal Size Curve')
        #loads = plotting.get_plot(loads, size=(10,2), title='Import / Export')

        #return render_template('results.html', 
        #                        report=report, 
        #                        curve=curve,
        #                        loads=loads,
        #                        sample_week=sample_week)
        
        return(1)



if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)

app.secret_key = os.urandom(12)
