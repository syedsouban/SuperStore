import json
from flask.app import Flask
from flask.globals import request
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from flask import Response
from utils._json import handle_mongoengine_response
from flask_socketio import SocketIO

from flask import Flask

import logging

app = Flask(__name__)



app.config["SECRET_KEY"] = "5d8b7997-de22-49a0-b76f-87da47d5b2ab"
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/superStoreDb"

app.config['MONGODB_SETTINGS'] = {
    'db': 'superStoreDb',
    'host': '127.0.0.1',
    'port': 27017
}
app.mongo = PyMongo(app)
app.APP_URL = "http://127.0.0.1:5000"
db:MongoEngine = MongoEngine(app)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    request_body = {}
    if request.get_json():
        request_body = request.get_json().copy()
    if request_body and "password" in request_body:
        del request_body["password"]
    app.logger.debug('Body: %s', json.dumps(request_body))

@app.after_request
def after_request_func(response):
    response.set_data(json.dumps(handle_mongoengine_response(response.get_json())).encode("utf-8"))
    return response

socketio = SocketIO()

socketio.init_app(app)

from routes import auth
from routes import category
from routes import product
# db = app.mongo.db

# with open("./schemas/category.json") as category_schema_file:
#     category_schema = json.load(category_schema_file)
#     cmd = OrderedDict([('collMod', 'categories'),
#                         ('validator', category_schema),
#                         ('validationLevel', 'moderate')])
#     collections = app.mongo.db.collection_names(False)
#     if 'categories' not in collections:
#         app.mongo.db.create_collection("categories")
#     app.mongo.db.command(cmd)

# with open("./schemas/product.json") as product_schema_file:
#     product_schema = json.load(product_schema_file)
#     cmd = OrderedDict([('collMod', 'products'),
#                         ('validator', product_schema),
#                         ('validationLevel', 'moderate')])
#     collections = app.mongo.db.collection_names(False)
#     if 'products' not in collections:
#         app.mongo.db.create_collection("products")
#     app.mongo.db.command(cmd)
    
