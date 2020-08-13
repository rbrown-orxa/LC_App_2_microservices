from flask import current_app, send_from_directory
import jsonschema
import json
import tempfile
import os

from ingest_file import process_load_file


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
    process_load_file(path_in=raw_path, lat=lat, lon=lon, path_out=processed_path)

    return ( {'handle':os.path.basename(processed_path)} )


def _optimise(request):
    with open('my-schema.json', 'r') as schema_file:
        schema = json.load(schema_file)
    content = request.json
    try:
        jsonschema.validate(instance=content, schema=schema)
        return content
    except Exception as err:
        assert False, f'422 {err}'


def _download(handle):
    return send_from_directory(
        current_app.config['UPLOAD_PATH'],
        handle, 
        as_attachment=True)


def _file_requirements():
    return { 'max_size_bytes': current_app.config['MAX_CONTENT_LENGTH'],
             'valid_extensions': current_app.config['UPLOAD_EXTENSIONS'] }
