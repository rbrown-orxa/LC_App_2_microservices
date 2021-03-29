from flask import Flask, url_for, abort, redirect

import tasks


app = Flask(__name__)


@app.route('/')
def index():
    return 'hello'


@app.route('/task')
def task():
    res = tasks.add.delay(2, 3)
    callback_url = url_for('task_callback', task_id=res.task_id)
    return {}, 202, {'Location': callback_url}


@app.route('/task_callback/<task_id>')
def task_callback(task_id):
    res = tasks.app.AsyncResult(task_id)
    status = res.status
    rv, code = '', 202
    if status == 'SUCCESS':
        rv, code = res.get(), 200
    elif status == 'FAILURE':
        code = 500
    return {'Status': status, 'Result': rv}, code



if __name__ == '__main__':
    app.run(port=5000, debug=True)

 