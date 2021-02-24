from flask import Flask, request, g, send_from_directory, current_app
from flask_cors import CORS,cross_origin
import os
import logging
import tempfile
import time
from pathlib import Path
import pickle
from minio import Minio
from minio.error import S3Error
from uuid import uuid4
from retrying import retry
from io import BytesIO, StringIO
import pandas as pd

import config as cfg


import utils
import library
import config
import billing
import subscription
from ingest_file import process_load_file


#TODO: Get constants from env
MINIO_CONN_STR = 'localhost:9000'
MINIO_USER = 'minioadmin'
MINIO_PW = 'minioadmin'
MINIO_SECURE = False
MINIO_RAW_BUCKET = 'raw-uploads'
MINIO_CLEANED_BUCKET = 'cleaned-uploads'


@retry(wait_fixed=5000)
def make_bucket(bucket_name):
    #TODO: don't block on this forever if object store is down
    #TODO: set bucket retention policy
    print('connecting to minio')
    client = Minio(MINIO_CONN_STR, MINIO_USER, MINIO_PW, secure=MINIO_SECURE)
    try:
        client.make_bucket(bucket_name)
        print('connected')
    except S3Error:
        pass #bucket already exists

make_bucket(MINIO_RAW_BUCKET)
make_bucket(MINIO_CLEANED_BUCKET)


app = Flask(__name__)
app.config.from_object(config)
CORS(app)
utils.init_file_handler(app.config['UPLOAD_PATH'])


@app.route("/upload", methods=['POST'])
def _upload():
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

    return ( {'handle': cleaned_file_id, "raw_upload": raw_file_id} )


@app.route("/download/<handle>")
def _download(handle):
    return send_from_directory(
        current_app.config['UPLOAD_PATH'],
        handle, 
        as_attachment=True)



if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='localhost', port=5000, debug=True)
