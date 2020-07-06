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

#import pv_optimiser
import aggregated_load as agg




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

@app.route("/submit", methods=["POST"])
def get_data():
    if False:#not session.get('logged_in'):
        return render_template('login.html')
    else:
        
        #fields = ['no_of_buildings','lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price',
        #            'expected_life_yrs', 'roof_size_m2', 'azimuth', 'roofpitch']
        
        #Call allocate pv size by roof efficiency function
        #print("Allocate PV size based on roof efficiency")
        #optimal_size,load = load_allocation.pv_allocate_size_by_roof_eff_optimiser(request)
        
        
        #Call aggregated load profile function
        #print("Allocate PV size based on aggregated load profile based on average roof paramters")
        #optimal_size,load = load_allocation.pv_aggregated_load_profile_optimiser(request)
        #print(optimal_size)
        #print(load)
        
        #print(optimal_size)
        #print(load)
        
        load = agg.sum_of_base_load_and_ev_load(request,"roofeff")
        
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
