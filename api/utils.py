import os
import functools
import pandas as pd
import config as cfg
import optimise
import sys
import logging
import time
from pathlib import Path
import pickle
from functools import wraps
from six.moves.urllib.request import urlopen
import json
from jose import jwt
from flask import request, g, _request_ctx_stack


def pickle_results(results, subscription_id, path):
    filename = 'results_' + subscription_id + '_' + \
                str(int(time.time() * 1000)) + '.pkl'
    logging.info(f'Pickling results to file: {filename}')
    
    path = os.path.join( path, 'results')
    Path(path).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join( path, filename)

    with open(filepath, 'wb') as file:
        pickle.dump(results, file, protocol=4)


def handle_exceptions(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                logging.exception('handling an error')
                # print(traceback.format_exc(err))
                return handle(err)
        def handle(err):
            msg = str(err).split('\n')[0]
            code = msg.split()[0]
            if code.isnumeric():
                return ( {'error':msg}, code )
            return ( {'error':msg}, 500 )
        return wrapper


def call_trace():
    parent = sys._getframe(2).f_code.co_name
    child = sys._getframe(1).f_code.co_name
    logging.warning(f'{child} called by {parent}')


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

def get_fixed_fields(schema, 
    fields=['lon', 'lat', 'cost_per_kWp', 
           'import_cost_kwh','export_price_kwh',
           'pv_cost_kwp', 'pv_life_yrs', 
           'battery_life_cycles', 'battery_cost_kwh',
           'load_profile_csv_optional']):
    """
    Retrieve the constant values from LC app form fields.
    req: the dict-like request object passed by Flask
    fields: list of the expected keys in req.form
    Returns: Dictionary of {expected form fields:field values}
    """
    return ( {field : schema.get(field, None) for field in fields} )

def get_form_data(schema,fixed_fields,variable_fields):
    
    fixed_data = get_fixed_fields(schema,fixed_fields)
    
    variable_data = get_variable_fields(schema,variable_fields)

    return({**fixed_data,**variable_data})


def get_variable_fields(schema,
        fields=['roof_size_m2', 'azimuth_deg','pitch_deg']):
    """
    Retrieve the variable values form fields.
    req: the dict-like request object passed by Flask
    fields: list of the expected keys in req.form
    Returns: Dictionary of {expected form fields:field values}
    """
    building_data=schema.get('building_data')
    super_dict = {}
    for d in building_data:
        for k, v in d.items():
            super_dict.setdefault(k, []).append(v)
    return ( {field : super_dict.get(field, None) for field in fields} )



def get_consumption_profile(file,consumption_kwh,building_type):
    
    if building_type == "domestic":
        df = pd.read_csv(file, header=0,usecols=['domestic_kW'])
        df = df*consumption_kwh
        df.rename(columns={'domestic_kW':'kWh'},inplace=True)
    else:
        df = pd.read_csv(file, header=0,usecols=['non_domestic_kW'])
        df = df*consumption_kwh
        df.rename(columns={'non_domestic_kW':'kWh'},inplace=True)
   
    df.index.name='hours'
    
    return(df)

def get_generation_1kw(form_data):
    
    """
    Generation 1Kw based on the aggregated load
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    #Get lat/lon
    lat, lon = float(form_data['lat']), float(form_data['lon'])
    
    
    #Get list of roof size, roof pitch, azimuth
    roofpitch, azimuth = ( 
        form_data['pitch_deg'].copy(),
        form_data['azimuth_deg'].copy() )
    generation_1kw = [] # list of df
    

    # NOTE: API called once per building below
    for pitch, azim in zip(roofpitch, azimuth):
        tmp_gen = optimise.generation_1kw(lat=lat, lon=lon,
                                          roofpitch=pitch, azimuth=azimuth)
        #TODO: Select start_date correctly

        generation_1kw.append(tmp_gen)
        
    return(generation_1kw)



def optimise_pv_size(generation_1kw,aggr_load,form_data):
    
    """
    optimise PV size based on the aggregated load
    
    generation_1kw: hourly generation in kWh per kWp installed capacity
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    cost_per_kWp = float(form_data['pv_cost_kwp'])
    import_cost = float(form_data['import_cost_kwh'])
    export_price = float(form_data['export_price_kwh'])
    expected_life_yrs = float(form_data['pv_life_yrs'])
    panel_efficiency = 0.18 
    # https://www.solar.com/learn/solar-panel-efficiency/
    
    roof_size_m2 = form_data['roof_size_m2'].copy()

    list_of_optimal_size = []
    list_of_df_cost_curve = []

    # for index in range(num):
    for gen_1_kw, load_kwh, roof_size_m2 in zip(
            generation_1kw, aggr_load, roof_size_m2):
        df_cost_curve = optimise.cost_curve(
                                generation_1kw=gen_1_kw,
                                load_kwh=load_kwh,
                                cost_per_kWp=cost_per_kWp,
                                import_cost=import_cost,
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                                roof_size_kw=roof_size_m2 * panel_efficiency)
        list_of_df_cost_curve.append(df_cost_curve)
        tmp_opt_size, optimal_revenue = optimise.optimise(df_cost_curve) 
        list_of_optimal_size.append(tmp_opt_size) 
     
    list_of_df = []    
    for gen_1_kw,load_kwh,size in zip(
            generation_1kw,
            aggr_load,
            list_of_optimal_size):  
        tmp_df = optimise.cost_saved_pa(
                                generation_1kw=gen_1_kw, 
                                load_kwh=load_kwh,
                                capacity_kWp = size,
                                cost_per_kWp=cost_per_kWp, 
                                import_cost=import_cost, 
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                      return_raw_data=True)
        list_of_df.append(tmp_df)
    
    return(list_of_optimal_size,list_of_df,list_of_df_cost_curve)

# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Validate the header provided in the token
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        assert False, '401 Invalid authorization header'
    elif len(parts) == 1:
        assert False, '401 Invalid header no token'
    elif len(parts) > 2:
        assert False, '401 Invalid header token'

    token = parts[1]
    return token

# Validat the access token by verifying the signature based upon the certificate used to sign it
def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):

        if not cfg.REQUIRE_AUTH:
            return f(*args, **kwargs)

        try:
            token = get_token_auth_header()
            jsonurl_b2c = urlopen("https://" + \
                              cfg.TENANT_NAME + ".b2clogin.com/" + \
                              cfg.TENANT_NAME + ".onmicrosoft.com/" + \
                              cfg.B2C_POLICY + "/discovery/v2.0/keys")
                
            jsonurl_ad = urlopen("https://" + "login.microsoftonline.com/" + \
                              "common" + "/discovery/v2.0/keys")
                
            #get unverified header from accesstoken
            unverified_header = jwt.get_unverified_header(token)
            #get unverified claims from accesstoken
            unverified_claims = jwt.get_unverified_claims(token)
            #get iss key value
            val = unverified_claims['iss'].find('b2clogin')
            #get public keys
            jwks = json.loads(jsonurl_b2c.read()) if val > 0 else json.loads(jsonurl_ad.read())
            #assign tenent name directory
            tenant = 'b2c' if val > 0 else 'ad'
            #get tenantid
            if val < 0:
                tid = unverified_claims['tid']
            #select audience
            aud = cfg.CLIENT_ID if val > 0 else cfg.CLIENT_ID_AD_MULT
            #select issuer
            iss = "https://" + cfg.TENANT_NAME + \
                    ".b2clogin.com/" + cfg.TENANT_ID + "/v2.0/" if val > 0 else \
                    "https://login.microsoftonline.com/" + tid + "/v2.0" 
            #store key values in dictionary
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
        except Exception:
            raise AuthError({"code": "invalid_header",
                             "description":
                             "Unable to parse authentication"
                             " token."}, 401)
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=aud,
                    issuer=iss
                )
                
            except jwt.ExpiredSignatureError:
                assert False, '401 token_expired'
            except jwt.JWTClaimsError:
                assert False, '401 invalid_claims'
            except Exception:
                assert False, '401 invalid_header'
            _request_ctx_stack.top.current_user = payload

            g.oid = payload['oid']
            g.tenant = tenant
            
            return f(*args, **kwargs)
        assert False, '401 invalid_header'
    return decorated


if __name__ == '__main__':
    
    from api_mock import *
    
    fixed_fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost_kwh', 
              'export_price_kwh','pv_cost_kwp', 'pv_life_yrs', 
              'battery_life_cycles', 'battery_cost_kwh',
                   'load_profile_csv_optional']
    
    variable_fields = ['roof_size_m2', 'azimuth_deg','pitch_deg']
      
    logging.info(str( get_form_data(
        request.json,fixed_fields,variable_fields ) ))
        
    logging.info(str( get_consumption_profile(
        cfg.PROFILES_BUILDING,1000,'domestic') ))



