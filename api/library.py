from flask import current_app, send_from_directory
import jsonschema
import json
import tempfile
import os
import logging
import requests
import utils
from ingest_file import process_load_file
import handle_base_loads
from results import get_optimise_results
from utils import get_fixed_fields
import config as cfg
import pandas as pd


def _upload(request):
    logging.info('handling file upload request')
    file = request.files.get('file', None)
    lat, lon = ( request.form.get(num, None) for num in ['lat', 'lon'] )

    assert all ([ lat, lon ]), '400 lat and lon fields required'
    assert file and file.filename, '422 No file provided'
    extension = os.path.splitext(file.filename)[1]

    assert extension in current_app.config['UPLOAD_EXTENSIONS'], \
            '415 Unsupported Media Type'

    fd, raw_path = tempfile.mkstemp(dir=current_app.config['UPLOAD_PATH'])
    with open(fd, 'wb') as temp_file:
        file.save(temp_file)

    fd, processed_path = tempfile.mkstemp(
        dir=current_app.config['UPLOAD_PATH'])
    df = process_load_file(path_in=raw_path, lat=lat, lon=lon)
    
    df.to_csv(processed_path, index=False)

    return ( {'handle':os.path.basename(processed_path)} )


def _optimise(request):

    logging.debug('starting optimisation')
    content = request.json

    with open('my-schema.json', 'r') as schema_file:
        schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=content, schema=schema)
    except Exception as err:
        assert False, f'422 {err}'

    results = get_optimise_results(content)
    return results        



def _download(handle):
    return send_from_directory(
        current_app.config['UPLOAD_PATH'],
        handle, 
        as_attachment=True)


def _file_requirements():
    return { 'max_size_bytes': current_app.config['MAX_CONTENT_LENGTH'],
             'valid_extensions': current_app.config['UPLOAD_EXTENSIONS'] }
    

def _consumption(request):
    
    annual_kwh_consumption,building_type = (
        request.form.get(num, None) 
        for num in [
                    'annual_kwh_consumption_optional',
                    'building_type'] )
    
    assert all ([ 
                annual_kwh_consumption, 
                building_type ]), \
                '400 annual_kwh_consumption and ' \
                + 'building_type fields required' 
    
    annual_kwh_consumption = float(annual_kwh_consumption)
    assert isinstance(building_type, str)
    
    rv = utils.get_consumption_profile( 
            current_app.config['PROFILES_BUILDING'],
            annual_kwh_consumption,
            building_type )
        
    return rv.to_json()

def _make_body(planid, qty):
    body = {'quantity': qty,
            'planId': planid}
    return json.dumps(body)


def _make_headers(uuid):
    headers = {'Content-type': 'application/json',
                'x-ms-requestid': '',
                'x-ms-correlationid': '',
                'authorization': 'Bearer ' + _get_authorization_token()}
    return headers

def _get_authorization_token():
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    body = {'grant_type': 'client_credentials',
            'client_id': cfg.CLIENT_ID_AD,
            'client_secret': cfg.CLIENT_SECRET,
            'resource':cfg.RESOURCE}
    r = requests.get(cfg.END_POINT,
                     data = body,
                     headers=headers)
    assert r.status_code == 200
    res = json.loads(r.content.decode())
    return(res['access_token'])
 

def _activate(request):
    
   dict = get_fixed_fields(request.json,fields=['SubscriptionId','PlanId','Quantity'])
   sid = dict['SubscriptionId']
   
   r = requests.post(
                cfg.FULLFILLMENT_URI + sid + '/activate',
                data=_make_body(dict['PlanId'], dict['Quantity']),
                params={'api-version': '2018-08-31'},
                headers=_make_headers(sid))
   return ( "OK" if r.status_code == 200 else "NOK")


def _get_annual_kwh(request):

    content = request.json
    building_type = content['building_type']

    try:
        annual_kwh = float( pd.read_csv(cfg.ANNUALS_BUILDING) [building_type] )
    except(KeyError):
        assert False, f'422 Building type \"{building_type}\" not found'
        
    return {'building_type':building_type, 'default_annual_kwh':annual_kwh}   
        
