from flask import Flask, request
import werkzeug
import jsonschema
import json
import tempfile
import os

app = Flask(__name__)
with open('my-schema.json', 'r') as schema_file:
	schema = json.load(schema_file)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5 # limit file upload size to 5 MB
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_PATH'] = 'tmp'

@app.route("/")
def index():
	return {'hello':'world'}


@app.route("/api")
def api():
	try:
		return handle_api(request)
	except:
		return ({'error':'unexpected server error'}, 500)


@app.route("/upload", methods=['POST'])
def upload():
	try:
		file = request.files.get('file', None)
		return handle_upload(file)
	except werkzeug.exceptions.RequestEntityTooLarge:
		return ( {'error':'file size too big'}, 400 )
	except:
		return ( {'error':'file upload error'}, 500 )
		

def handle_upload(file):
	if file is None:
		return ({'error':'no file'}, 400)
	if file.filename == '':
		return ({'error':'no filename'}, 400)
	if os.path.splitext(file.filename)[1] not in app.config['UPLOAD_EXTENSIONS']:
		return ({'error':'incorrect file type'}, 400)
	if not os.path.exists(app.config['UPLOAD_PATH']):
		os.mkdir(app.config['UPLOAD_PATH'])
	fd, path = tempfile.mkstemp(dir=app.config['UPLOAD_PATH'])
	with open(fd, 'wb') as temp_file:
		file.save(temp_file)
	return ( {'handle':os.path.basename(path)} )


def handle_api(request):
	try:
		content = request.json
		jsonschema.validate(instance=content, schema=schema)
	except werkzeug.exceptions.BadRequest as err:
		return ({'error':f'invalid json: {err}'}, 400)
	except jsonschema.exceptions.ValidationError as err:
		return ({'error':err.message}, 400)
	return content


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)


