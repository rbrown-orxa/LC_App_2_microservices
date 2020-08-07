from flask import Flask, request, send_from_directory
import werkzeug
import jsonschema
import json
import tempfile
import os
import functools

app = Flask(__name__)
with open('my-schema.json', 'r') as schema_file:
	schema = json.load(schema_file)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5 # limit file upload size to 5 MB
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_PATH'] = 'tmp'

if not os.path.exists(app.config['UPLOAD_PATH']):
	os.mkdir(app.config['UPLOAD_PATH'])


def handle_exceptions(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as err:
				return handle(err)
		def handle(err):
			msg = str(err).split('\n')[0]
			code = msg.split()[0]
			if code.isnumeric():
				return ( {'error':msg}, code )
			return ( {'error':msg}, 500 )
		return wrapper


@app.route("/")
def index():
	return {'hello':'world'}


@app.route("/api")
@handle_exceptions
def api():
	return handle_api(request)


@app.route("/upload", methods=['POST'])
@handle_exceptions
def upload():
	file = request.files.get('file', None)
	return handle_upload(file)

		
@app.route("/download/<handle>")
@handle_exceptions
def download(handle):
	return send_from_directory(app.config['UPLOAD_PATH'],
		handle, as_attachment=True)	


def handle_upload(file):
	assert file and file.filename, '422 No file provided'
	extension = os.path.splitext(file.filename)[1]
	assert extension in app.config['UPLOAD_EXTENSIONS'], '415 Unsupported Media Type'

	fd, path = tempfile.mkstemp(dir=app.config['UPLOAD_PATH'])
	with open(fd, 'wb') as temp_file:
		file.save(temp_file)
	return ( {'handle':os.path.basename(path)} )


def handle_api(request):
	content = request.json
	try:
		jsonschema.validate(instance=content, schema=schema)
		return content
	except Exception as err:
		assert False, f'422 {err}'



if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)


