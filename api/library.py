from flask import current_app, send_from_directory
import jsonschema
import json
import tempfile
import os
import logging

import utils
from ingest_file import process_load_file
import handle_base_loads
from results import get_optimise_results


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
 

def _activate(request):
    
   file = os.path.abspath('tmp') + '\data.json'
    
   with open(file, "w") as f:
       json.dump(request.json, f)
        
   return ( {'handle':os.path.basename(file)} )
        

