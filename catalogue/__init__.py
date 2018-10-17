import os
import sys
import json

from flask import Flask, render_template
from jinja2 import Markup
from flask_assets import (Environment, Bundle)
from htmlmin.minify import html_minify


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)

    def include_raw(filename, squash=''):
        with app.open_resource('templates/{}'.format(filename),mode='r') as f:
            return Markup(f.read().replace('\n', squash))


    def include_json(*filenames):
        data={}
        for filename in filenames:
            with app.open_resource(os.path.join('templates',filename),mode='r') as f:
                data.update(json.loads(f.read()))
        return Markup(json.dumps(data, separators=[',',':']))

    @app.context_processor
    def inject_include_raw():
        return dict(include_raw=include_raw, include_json=include_json)

    create_mustache_templates(app)

    @app.route('/')
    def index():
        return html_minify(render_template('index.html'))


    if app.config['DEBUG']:
        app.after_request(bust_cache)

    register_assets(app)

    return app

def create_mustache_templates(app):
    with app.app_context():
        with open(os.path.join(app.static_folder,'js','setup.js'),mode='w') as f:
            f.write(render_template('setup.js'))

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
        'js/setup.js',
        'js/pipeline.js',
        filters='jsmin',
        output='packed.js'
    )
    assets.register('js_all', js)

    css = Bundle(
        'css/bootstrap.min.css',
        'css/jquery-ui.min.css',
        'css/style.css',
        output='packed.css'
    )
    assets.register('css_all', css)