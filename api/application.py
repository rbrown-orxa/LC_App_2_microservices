from flask import Flask, request, send_from_directory
from flask_selfdoc import Autodoc
import os

import utils
import library
import config


app = Flask(__name__)
app.config.from_object(config)
auto = Autodoc(app)
utils.init_file_handler(app.config['UPLOAD_PATH'])


@app.route("/upload", methods=['POST'])
@auto.doc()
@utils.handle_exceptions
def upload():
    """Upload a file for later use
    File properties must comply with /file_requirements
    Return:
    application/json
    { "handle" :str } if successful.
    { "error": str } if not successul."""
    return library._upload(request)


@app.route("/api")
@auto.doc()
@utils.handle_exceptions
def api():
    """Optimise a solar and battery system size
    Request: According to /schema
    Return:
    application/json
    According to /result_schema
    """
    return library._api(request)


@app.route("/schema")
@auto.doc()
def schema():
    """Get api request json-schema definition"""
    return utils._schema()
        

@app.route("/download/<handle>")
@auto.doc()
@utils.handle_exceptions
def download(handle):
    """Retrieve a file by it's <handle>:str
    Return:
    application/octet-stream
    """
    return library._download(handle)


@app.route("/file_requirements")
@auto.doc()
def file_requirements():
    """Get requirements for uploaded files
    Return:
    application/json
    { "max_size_bytes": num, "valid_extensions": [str, str, ...] }
    Example:
    { "max_size_bytes": 5242880, "valid_extensions": [ ".csv" ] }"""
    return library._file_requirements()


@app.route('/')
def documentation():
    return auto.html()


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='localhost', port=5000, debug=True)

app.secret_key = os.urandom(12)


