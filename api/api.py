from flask import Flask, request
import werkzeug
import jsonschema
import json
import tempfile


app = Flask(__name__)
with open('my-schema.json', 'r') as schema_file:
	schema = json.load(schema_file)


@app.route("/")
def index():
	return {'hello':'world'}


@app.route("/api")
def api():
	try:
		return handle_api(request)
	except:
		return ({'error':'unexpected server error'}, 500)


@app.route("/upload")
def upload():
	file = request.files.get('file', None)
	if file is not None:
		return handle_upload(file)
	else:
		return ({'error':'no file'}, 400)


def handle_upload(file):
	temp_filename = tempfile.mktemp(suffix='.csv')
	print(f'Temporary file will be created at {temp_filename}')
	with open(temp_filename, 'wb') as temp_file:
		file.save(temp_file)
	return ( {'file':temp_filename} )


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


