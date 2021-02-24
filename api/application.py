from flask import Flask, request, g, send_from_directory
from flask_cors import CORS,cross_origin
from flask_selfdoc import Autodoc
import os
import logging
import time
from pathlib import Path
import pickle
from utils import get_fixed_fields,make_input_tables

import config as cfg


if cfg.DEBUG_MODE:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

FORMAT = '%(asctime)-s\t%(levelname)-s\t%(filename)-s\t' +\
         '%(funcName)-s\tLine:%(lineno)-s\t\t\'%(message)s\''
logging.basicConfig(level=log_level, format=FORMAT)


import utils
import library
import config
import billing
import subscription

app = Flask(__name__)
app.config.from_object(config)
CORS(app)
auto = Autodoc(app)
utils.init_file_handler(app.config['UPLOAD_PATH'])

# if app.config['APPLY_BILLING']:
#     billing.make_tables(app.config['BILLING_DB_CONN_STR'])
    
if app.config['APPLY_DEFAULT_VALUES']: 
    make_input_tables(app.config['BILLING_DB_CONN_STR'])



@app.route("/optimise", methods=['GET','POST'])
@utils.handle_exceptions
@auto.doc()
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
# @utils.requires_auth
def optimise():
    """Optimise a solar and battery system size

    Request:
        Content-Type: application/json
        Body: According to /schema

    Return:
        Content-Type: application/json
        According to /result_schema
    """    

    logging.info('got an optimise request')
    logging.info(f'json input schema: {request.json}')

    lat = request.json.get('lat', None)
    lon = request.json.get('lon', None)
    query_id = billing.query_started(lat, lon)
    # breakpoint()

    rv = library._optimise(request)

    if app.config['PICKLE_RESULTS']:
        utils.pickle_results(rv, sub_id, app.config['UPLOAD_PATH'])
    
    billing.query_successful(query_id)

    return (rv,
            200, 
            {'Content-Type': 'application/json; charset=utf-8'})


@app.route("/upload", methods=['POST'])
@auto.doc()
@utils.handle_exceptions
def upload():
    """Upload a file for later use
    File properties must comply with /file_requirements

    Request:
        Content-Type: multipart/form-data

        Content-Disposition: form-data; name="file"; 
            filename="Factory_Heavy_loads_15min.csv"
        Content-Type: text/csv
        ProductDataStreamId,ReportedDateTime,RealPower1,RealPower2,RealPower3
        964352,2019-03-01_00:00:50,85.7043,100.6254,47.9806
        964361,2019-03-01_00:15:50,1013.299,2106.9419,83.0753
        ...        

        Content-Disposition: form-data; name="lat"
        18.495858
        
        Content-Disposition: form-data; name="lon"
        73.883544

    Return:
        Content-Type: application/json
        { "handle" :str } if successful.
        { "error": str } if not successul."""
    return library._upload(request)


@app.route("/activate", methods=['POST'])
@auto.doc()
@utils.handle_exceptions
def activate():
   """Activate new subscription using Azure Market place SaaS fullfillment
     API when the user submits for our offer

    Request:
        Content-Type: application/json
        Body: According to /activate

    Return:
        Content-Type: application/json
        Response code
    """
     
   return library._activate(request)





@app.route("/schema")
@auto.doc()
def schema():
    """Get api request json-schema definition

    Request:
        Body: none
    Return:

        Content-Type: application/json
        Body: json-schema definition
    """
    return utils._schema()


@app.route("/result_schema")
@auto.doc()
def result_schema():
    """Get api /optimise result json-schema definition

    Request:
        Body: none
    Return:

        Content-Type: application/json
        Body: json-schema definition
    """
    return utils._result_schema()
        

@app.route("/download/<handle>")
@auto.doc()
@utils.handle_exceptions
def download(handle):
    """Retrieve a file by it's <handle>:str

    Request:
        Body: none

    Return:
        Content-Type: application/octet-stream
        Content-Disposition: attachment; filename=example_handle
    """
    return library._download(handle)


@app.route("/file_requirements")
@auto.doc()
def file_requirements():
    """Get requirements for uploaded files

    Request:
        Body: none

    Return:
        Content-Type: application/json
        Body:
        { "max_size_bytes": num, "valid_extensions": [str, str, ...] }

    Example:
        { "max_size_bytes": 5242880, "valid_extensions": [ ".csv" ] }"""
    return library._file_requirements()


@app.route("/consumption")
@auto.doc()
def consumption():
    """Get api request consumption profile

     Request:
        Content-Type: multipart/form-data
        
        Content-Disposition: form-data; name="annual_kwh_consumption_optional"
        2400
        
        Content-Disposition: form-data; name="building_type"
        domestic/work/public/commercial/delivery

    Return:
        Content-Type: application/json
        { "error": str } if not successul.    """
 
    return library._consumption(request)

@app.route("/resolve", methods=['GET','POST'])
@utils.handle_exceptions
@auto.doc()
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@utils.requires_auth
def resolve():
    """Resolve the user by decoding accesstoken sent by request header. 
    The objectid in case of ad account user will be checked if the user has 
    active subscription and plan id. If there are no active subscription or 
    user has not susbcribed to our offer then user will be allowed free quote 
    equal to configured value of MAX_FREE_CALL. 
    In case of b2c account user will be allowed free quote 
    equal to configured value of MAX_FREE_CALL

    Request:
        Content-Type: application/json
        Body: According to /schema

    Return:
        Content-Type: application/json
        According to /usage_schema
        Body:
        { "object_id": uuid, "subscription_id': uuid, "plan_id": str,
          "free_calls": int, "max_free_calls": int}
    """

    object_id, tenant, sub_id, plan_id, used_no, max_no, domain = None, None, None, None, None, None, None
    if app.config['REQUIRE_AUTH']:
   	    # object_id = request.json['oid'] # get oid from request.json
        
       	object_id = g.oid # get oid from JWT claim instead of request.json
       	tenant = g.tenant
        domain = g.domain
        logging.info(f'got oid: {object_id}')
       	sub_id, plan_id, used_no, max_no = billing.check_subscription(object_id, tenant, domain)
            
    return {'object_id': object_id,'subscription_id':sub_id,'plan_id':plan_id, 'free_calls': used_no, \
            'max_free_calls':max_no}


@app.route("/default_annual_kwh")
@auto.doc()
@utils.handle_exceptions
def default_annual_kwh():
    """Get default annual kwh consumption for a building type.

    Request:
        Body: {"building_type":building_type}
    Return:
        Content-Type: application/json
        Body: {"building_type": building_type, "default_annual_kwh": int}
    Example:
        {"building_type":"domestic"}
    """
    return library._get_annual_kwh(request)



@app.route("/default_country_values", methods=['GET','POST'])
@utils.handle_exceptions
@auto.doc()
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@utils.requires_auth
def default_country_values():
    """get default values for a country using lat/Lon and building type

    Request:
        Content-Type: application/json
        Body: According to /schema

    Return:
        Content-Type: application/json
        According to /usage_schema
        Body: Dictionary of default country values
    """
     
    logging.info(f'default country values json input: {request.json}')
    return library._get_country_values(request)    


@app.route('/')
def documentation():
    return auto.html()


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='localhost', port=5000, debug=True)

app.secret_key = os.urandom(12)
