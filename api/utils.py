import os
import functools
from markdown import markdown


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


def init_file_handler(upload_path):
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)


def _schema():
    with open('my-schema.json') as file:
        schema = file.read()
    return schema