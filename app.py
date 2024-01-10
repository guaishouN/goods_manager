# this is flask hello app
# deploy on windows by using waitress like this: 
# waitress-serve --host=0.0.0.0 --port=5000 --call 'app:create_app'
# deploy on linux by using gunicorn like this:
# gunicorn -b --bind=5000 --host=0.0.0.0 --workers=4 --threads=2 --timeout=60 app:app

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/adr2/0000001')
@cross_origin()
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
@cross_origin()
def favicon():
    return app.send_static_file('favicon.ico')

