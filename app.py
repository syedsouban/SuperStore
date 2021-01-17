# import eventlet
# eventlet.monkey_patch()
import json
from flask.app import Flask
from flask.globals import request
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from flask import Response
from utils._json import handle_mongoengine_response
# from flask_socketio import SocketIO
import os

from flask import Flask
from flask.wrappers import Response
from flask_uploads import UploadSet, IMAGES, configure_uploads
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
app.APP_URL = "http://0.0.0.0:80"
db:MongoEngine = MongoEngine(app)

app.config["PORT"] = os.environ.get("PORT")
print("port number is "+os.environ.get("PORT"))
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
logging.root.setLevel(logging.INFO)

app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

@app.before_request
def log_request_info():
    server_number = app.config["PORT"]
    logging.info('Headers: %s', request.headers)
    logging.info("Server %s is handling the request!"%server_number)
    print("Server %s is handling the request"%server_number)
    request_body = {}
    if request.get_json():
        request_body = request.get_json().copy()
    if request_body and "password" in request_body:
        del request_body["password"]
    logging.info('Body: %s', json.dumps(request_body))

@app.after_request
def after_request_func(response):
    if type(response) == Response and response.get_json():
        response.set_data(json.dumps(handle_mongoengine_response(response.get_json())).encode("utf-8"))
    return response

@app.route("/which", methods=["GET"])
def root():
    server_number = app.config["PORT"]
    return "This is the superstore backend api %s server"%server_number

# socketio = SocketIO(logger=True,engineio_logger=True,cors_allowed_origins='*',message_queue='redis://127.0.0.1:6379')
# socketio = SocketIO(cors_allowed_origins='*')
# socketio.init_app(app,message_queue='redis://')

from routes import auth
from routes import category
from routes import product
# from routes import chat
# app.register_blueprint(chat.bp)
# from events import events

# if __name__ == "__main__":
#     socketio.run(app)

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
    
