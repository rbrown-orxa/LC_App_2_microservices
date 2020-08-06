from flask import Flask, request, url_for, send_file, Markup
from flask import Flask, flash, redirect, render_template, request, session, abort,url_for,send_file, Markup
import matplotlib
from io import BytesIO, StringIO
import io
import os
import tempfile
from flask import render_template
import nbimporter

import uuid
import requests
#from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import app_config

import plotting
import pv_optimiser

matplotlib.use('Agg')


app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('form.html', user=session["user"], version=msal.__version__)

@app.route("/login")
def login():
    session["state"] = str(uuid.uuid4())
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    auth_url = _build_auth_url(scopes=app_config.SCOPE, state=session["state"])
    return render_template("login.html", auth_url=auth_url, version=msal.__version__)


#@app.route('/')
#def home():
#    if not session.get('user'):
#        return redirect(url_for("login"))
#    else:
#        return render_template('index.html', user=session["user"], version=msal.__version__)


#@app.route('/login', methods=['POST'])
#def do_admin_login():
#    if request.form['password'] == 'password' and request.form['username'] == 'admin':
#        session['logged_in'] = True
#        return render_template('form.html')
#    else:
#        flash('wrong password!')
#        return home()


#@app.route("/logout")
#def logout():
#    session['logged_in'] = False
#    return home()
	
	
@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("index"))  # No-OP. Goes back to index page
    if "error" in request.args:  # Authentication/Authorization failure
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for("authorized", _external=True))
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_url=_build_auth_url)  # Used in template

	
	
@app.route("/help")
def help():
    return render_template('help.html')
	
@app.route("/PrivacyPolicy")
def PrivacyPolicy():
    return render_template('PrivacyPolicy.html')
	

@app.route("/submit", methods=["POST"])
def get_data():


    try:
        fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price',
                    'expected_life_yrs', 'roof_size_m2', 'azimuth', 'roofpitch']
        form_data = {}
        for field in fields:
            form_data[field] = request.form.get(field, None)
            print('ffields',form_data[field])
        file = request.files.get('file', None)
        
        if 'debug_api' in request.form:
            return(form_data)
        
        temp_filename = tempfile.mktemp(suffix='.csv')
        
        print(f'Temporary file will be created at {temp_filename}')
        
        with open(temp_filename, 'wb') as temp_file:
            file.save(temp_file)
            
        curve, loads, report = pv_optimiser.api(form_data, temp_filename)
        
        os.remove(temp_filename)
        
        print(f'Temporary file removed: {temp_filename}')
        raw_loads = loads.to_json()
        raw_curve = curve.to_json()
        raw_sample_week = loads.iloc[:24*7,:].to_json()
        
        sample_week = plotting.get_plot(
            loads.iloc[:24*7,:], size=(14,4), title='Sample Week',
            xlabel='Date',
            ylabel='Power (kWh)')
        
        curve = plotting.get_plot(curve, size=(6,4),
                                    title='Optimal Size Curve',
                                    xlabel='System Size (kWp)',
                                    ylabel='Annual Profit')
                                    
        loads = plotting.get_plot(loads, size=(14,4),
                                    title='Import / Export',
                                    legends_list=['Solar PV generation (kWh)', 'Building load (kWh)', 'Imported power (kWh)', 'Exported power (kWh)'],
                                    xlabel='Date',
                                    ylabel='Power (kWh)')
                                    
                                    
        return render_template('results.html', 
                                report=report, 
                                curve=curve,
                                loads=loads,
                                sample_week = sample_week, 
                                raw_curve =  raw_curve,
                                raw_loads = raw_loads,
                                raw_sample_week = raw_sample_week)
    except BaseException as e:
        error = "Error: Please check whether the inputs are valid. Suggestion: 1. Check whether file is uploaded. 2. Location is selected from map. Additional message: "+ str(e)
        # retirect back to form page with error
        return render_template('form.html', error=error)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='localhost', port=port,debug=True)

app.secret_key = os.urandom(12)
