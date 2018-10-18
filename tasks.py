import os
from invoke import task
from catalogue import create_app
from flask_frozen import Freezer
from flask import Flask, render_template
from flask_htmlmin import HTMLMIN
import http.server
import socketserver

@task
def build(c):
    app = create_app()
    HTMLMIN(app)
    app.config['MINIFY_PAGE'] = True
    app.config['FREEZER_RELATIVE_URLS']=True
    app.config['FREEZER_REMOVE_EXTRA_FILES']=True
    app.config['FREEZER_DESTINATION']="../docs"
    app.config['FREEZER_STATIC_IGNORE']=['js/*','css/*','.webassets-cache/*']
    freezer = Freezer(app)
    freezer.freeze()

@task(pre=[build])
def teststatic(c):
    PORT=5000

    os.chdir('docs')
    Handler = http.server.SimpleHTTPRequestHandler
    c.run('ls')
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

@task
def run(c):
    app = create_app()
    #app.config['ENV']='development'
    #app.config['ASSETS_DEBUG']=True
    extra_dirs = ['.',]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            if dirname=='.webassets-cache' or dirname=='gen' or dirname=='.git':
                continue
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    app.run(host="0.0.0.0", port="5000", extra_files=extra_files, debug=True)
