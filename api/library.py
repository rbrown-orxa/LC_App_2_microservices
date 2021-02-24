from flask import current_app, send_from_directory, Response
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
from utils import get_fixed_fields, getplace, get_default_values
import config as cfg
import pandas as pd
from exchangeratesapi import Api as Currency_converter
from minio import Minio
from minio.error import S3Error
from uuid import uuid4
from io import BytesIO, StringIO


#TODO: Get constants from env
MINIO_CONN_STR = 'localhost:9000'
MINIO_USER = 'minioadmin'
MINIO_PW = 'minioadmin'
MINIO_SECURE = False
MINIO_RAW_BUCKET = 'raw-uploads'
MINIO_CLEANED_BUCKET = 'cleaned-uploads'




def _optimise(request):

    logging.debug('starting optimisation')
    content = request.json

    with open('my-schema.json', 'r') as schema_file:
        schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=content, schema=schema)
    except Exception as err:
        assert False, f'422 JSON validation error: {err}'

    results = get_optimise_results(content)
    return results        


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


def _get_country_values(request):
     
    content = request.json
    lat = content['lat']
    lon = content['lon']
    building_type = content['building_type']
    converter = Currency_converter()
    
    #get building type

    try:
        tmp_df = pd.read_csv(cfg.ANNUALS_BUILDING) [building_type]
        annual_kwh =int(tmp_df.to_numpy().mean())
    except(KeyError):
        assert False, f'422 Building type \"{building_type}\" not found'
     
    #get country name from lat/lon
    country = getplace(lat,lon)['country']
    
    #get currency code from country
    try:
        all_currency_codes = pd.read_csv(
            cfg.COUNTRY_DETAILS, index_col='Country')
        currency_code = all_currency_codes.Code[country]
    except(KeyError):    
        assert False, f'422 Currency Code \"{country}\" not found'
        
    #get exchange rate from exchange rate API
    try:
        exchange_rate_usd = converter.get_rate('USD', currency_code)
    except: 
        assert False, f'422 exchange rate error \"{country}\" not found'
        
    if (bool([ele for ele in building_type if(ele in 'domestic')]) ):
       building_type = 'domestic'
    else:
       building_type = 'commercial' 
    
    #get default values from postgre db    
    default_values = get_default_values(country,building_type,
                        annual_kwh, exchange_rate_usd, currency_code)
        

    return default_values



def _upload(request):

    logging.info('handling file upload request')
    file = request.files.get('file', None)
    lat, lon = ( request.form.get(num, None) for num in ['lat', 'lon'] )

    assert all ([ lat, lon ]), '400 lat and lon fields required'
    assert file and file.filename, '422 No file provided'
    extension = os.path.splitext(file.filename)[1]

    assert extension in current_app.config['UPLOAD_EXTENSIONS'], \
            '415 Unsupported Media Type'


    # Write raw file to bucket
    raw_file_id = str(uuid4())
    size = os.fstat(file.fileno()).st_size
    content_type = file.content_type
    client = Minio(MINIO_CONN_STR, MINIO_USER, "minioadmin", secure=False)
    client.put_object(
            MINIO_RAW_BUCKET, raw_file_id, file, size, content_type)

    # Read raw file from bucket into DataFrame and pre-process
    raw_file = client.get_object(MINIO_RAW_BUCKET, raw_file_id)
    raw_buf_b = BytesIO(raw_file.read())
    #TODO: Get encoding for use in decode() function below
    raw_buf_t = StringIO(raw_buf_b.read().decode())
    df = process_load_file(raw_buf_t, lat=lat, lon=lon)

    # Write cleaned file to bucket
    cleaned_file_id = str(uuid4())
    cleaned_file = df.to_csv(index=False).encode('utf-8')
    client.put_object(
            MINIO_CLEANED_BUCKET,
            cleaned_file_id,
            BytesIO(cleaned_file),
            len(cleaned_file),
            content_type='application/csv')
    rv = {'handle': cleaned_file_id, "raw_upload": raw_file_id}
    logging.info(f'processed uploaded files: {rv}')

    return ( rv )


def _download(handle):
    # raise NotImplementedError('Need to change this to use bucket')
    client = Minio(MINIO_CONN_STR, MINIO_USER, "minioadmin", secure=False)
    try:
        resp = client.get_object(MINIO_RAW_BUCKET, handle)
    except S3Error:
        resp = client.get_object(MINIO_CLEANED_BUCKET, handle)
    return Response(resp, content_type=resp.headers['Content-Type'])
    




