import os
from invoke import task
from config import create_app
from flask_frozen import Freezer
from flask import Flask

@task
def build(c):
    app = create_app()
    app.config['FREEZER_RELATIVE_URLS']=True
    app.config['FREEZER_DESTINATION']="../docs"
    freezer = Freezer(app)
    freezer.freeze()
    c.run('rm -rf docs/static/js docs/static/css')

@task(pre=[build])
def teststatic(c):
    app = Flask(__name__, static_folder='docs')
    app.run(host="0.0.0.0", port="5000")

@task
def run(c):
    app = create_app()
    app.config['ENV']='development'
    app.config['ASSETS_DEBUG']=True
    extra_dirs = ['.',]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    app.run(host="0.0.0.0", port="5000", extra_files=extra_files, debug=True)