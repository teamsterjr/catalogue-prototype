import os
import sys

from flask import Flask, render_template
from jinja2 import Markup
from flask_assets import (Environment, Bundle)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    def include_raw(filename):
        with app.open_resource('templates/{}'.format(filename),mode='r') as f:
           return Markup(f.read())

    @app.context_processor
    def inject_include_raw():
        return dict(include_raw=include_raw)

    @app.route('/')
    def index():
        return render_template('index.html')


    if app.config['DEBUG']:
        app.after_request(bust_cache)

    register_assets(app)

    return app

def bust_cache(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def register_assets(app):
    if app.config['DEBUG']:
        app.config['ASSETS_DEBUG'] = True

    assets = Environment(app)
    assets.set_url('static')
    js = Bundle(
        'js/jquery.js',
        'js/jquery-ui.min.js',
        'js/bootstrap.js',
        'js/handlebars.js',
        'js/pipeline.js',
        filters='jsmin',
        output='gen/js/packed.js'
    )
    assets.register('js_all', js)

    css = Bundle(
        'css/bootstrap.min.css',
        'css/jquery-ui.min.css',
        'css/style.css',
        output='gen/css/packed.css'
    )
    assets.register('css_all', css)