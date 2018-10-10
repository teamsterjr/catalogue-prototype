import os
from invoke import task
from config import create_app
from flask_frozen import Freezer

@task
def build(c):
    app = create_app()
    freezer = Freezer(app)
    freezer.freeze()
    c.run('rm -rf docs/static/js docs/static/css docs/static/.webassets-cache')

@task
def run(c):
    app = create_app()
    app.config['ENV']='development'
    extra_dirs = ['.',]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    app.run(host="0.0.0.0", port="5000", extra_files=extra_files)