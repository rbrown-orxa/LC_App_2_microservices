from flask import current_app, send_from_directory
import jsonschema
import json
import tempfile
import os

import utils
from ingest_file import process_load_file
import handle_base_loads


def _upload(request):
    file = request.files.get('file', None)
    lat, lon = ( request.form.get(num, None) for num in ['lat', 'lon'] )

    assert all ([ lat, lon ]), '400 lat and lon fields required'
    assert file and file.filename, '422 No file provided'
    extension = os.path.splitext(file.filename)[1]
    assert extension in current_app.config['UPLOAD_EXTENSIONS'], '415 Unsupported Media Type'

    fd, raw_path = tempfile.mkstemp(dir=current_app.config['UPLOAD_PATH'])
    with open(fd, 'wb') as temp_file:
        file.save(temp_file)

    fd, processed_path = tempfile.mkstemp(dir=current_app.config['UPLOAD_PATH'])
    df = process_load_file(path_in=raw_path, lat=lat, lon=lon)
    
    df.to_csv(processed_path, index=False)

    return ( {'handle':os.path.basename(processed_path)} )


def _optimise(request):
    development_rv = {
        'results': {

            'site':{
                'success': True, 
                'battery_size_kwh': 1.0,
                'annual_import_site_kwh': 1.0, 
                'annual_import_ev_kwh': 1.0,
                'annual_import_total_kwh': 1.0,
                'annual_import_with_pv_kwh': 1.0, 
                'annual_import_with_pv_and_battery_kwh': 1.0,
                'original_import_cost': 1.0, 
                'with_ev_import_cost': 1.0,
                'optimised_import_cost': 1.0
            },

            'buildings': [
                {'name':'building_1', 'pv_size_kw': 1.0, 'num_chargers':1},
                {'name':'building_2', 'pv_size_kw': 1.0, 'num_chargers':1},
                {'name':'building_3', 'pv_size_kw': 1.0, 'num_chargers':1},

            ]
        }
    }
    with open('my-schema.json', 'r') as schema_file:
        schema = json.load(schema_file)
    query = request.json
    assert isinstance(query, dict)
    try:
        jsonschema.validate(instance=query, schema=schema)
    except Exception as err:
        assert False, f'422 {err}'

    buildings = handle_base_loads.list_buildings(query)
    
    dummy_rv = json.dumps( development_rv )
    return dummy_rv


def _download(handle):
    return send_from_directory(
        current_app.config['UPLOAD_PATH'],
        handle, 
        as_attachment=True)


def _file_requirements():
    return { 'max_size_bytes': current_app.config['MAX_CONTENT_LENGTH'],
             'valid_extensions': current_app.config['UPLOAD_EXTENSIONS'] }
    

def _consumption(request):
    
    annual_kwh_consumption,building_type = ( request.form.get(num, None) for num in ['annual_kwh_consumption_optional','building_type'] )
    
    assert all ([ annual_kwh_consumption, building_type ]), '400 annual_kwh_consumption and building_type fields required'
    
    annual_kwh_consumption = float(annual_kwh_consumption)
    assert isinstance(building_type, str)
    
    rv = utils.get_consumption_profile( current_app.config['PROFILES_BUILDING'],
                                    annual_kwh_consumption,
                                    building_type )
        
    return rv.to_json()
        

