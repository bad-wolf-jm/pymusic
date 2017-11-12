from flask import Flask, Response
from flask import request  # , render_template
from flask_cors import CORS, cross_origin
import jinja2
import json
import os
import random
from threading import Thread
import psutil
import glob
import datetime
import time

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

loader = jinja2.FileSystemLoader(
    [os.path.join(os.path.dirname(__file__), "static"),
     os.path.join(os.path.dirname(__file__), "templates")])
environment = jinja2.Environment(loader=loader)


def render_template(template_filename, **context):
    return environment.get_template(template_filename).render(context)


if __name__ == '__main__':
    app.run()
