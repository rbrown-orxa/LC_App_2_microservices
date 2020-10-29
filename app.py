# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:33:51 2020

@author: Sanjeev Kumar
"""

from flask import Flask,render_template
from jinja2 import Environment, FileSystemLoader
import os
import pdfkit 
 
app = Flask(__name__)


env = Environment( loader = FileSystemLoader('./templates') )
template = env.get_template('index.html')

filename = os.path.join('./', 'html', 'index.html')

with open(filename, 'w') as fh:
    fh.write(template.render(
        condition = "happy"
    ))
    
pdfkit.from_file(filename, 'out.pdf')

@app.route('/')
def index():
    condition = "happy12"
    return render_template('index.html', condition=condition)
 
@app.route('/hello')
def hello():
    return 'Hello World'
 
app.run(host='localhost', port=5000)