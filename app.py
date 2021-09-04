import json
from flask.app import Flask
from flask.globals import request
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from flask import Response
from utils._json import handle_mongoengine_response


import os

from flask import Flask
from flask.wrappers import Response
from flask_uploads import UploadSet, configure_uploads, IMAGES
import logging

disable_socketio = os.environ.get("disable_socketio") == "true"


if not disable_socketio:
    from flask_socketio import SocketIO

app = Flask(__name__)

app.config["SECRET_KEY"] = "5d8b7997-de22-49a0-b76f-87da47d5b2ab"
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/superStoreDb"



app.config['MONGODB_SETTINGS'] = {
    'db': 'superStoreDb',
    'host': '127.0.0.1',
    'port': 27017
}
app.mongo = PyMongo(app)
# app.APP_URL = "http://0.0.0.0:80"
db:MongoEngine = MongoEngine(app)

app.config["PORT"] = os.environ.get("PORT")
#print("port number is "+os.environ.get("PORT"))
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_logger.handlers)
app.logger.setLevel(logging.DEBUG)

import arrow

from logging.handlers import TimedRotatingFileHandler
logname = "logs/SuperStore.log"
handler = TimedRotatingFileHandler(logname, when="D", interval=1)
logging.root.handlers.append(handler)
logging.root.setLevel(logging.INFO)

# import time
# rootLogger = logging.getLogger()
# fileHandler = logging.FileHandler("{0}/{1}.log".format("./",str(time.time())))
# rootLogger.addHandler(fileHandler)
# consoleHandler = logging.StreamHandler()
    # consoleHandler.setFormatter(logFormatter)
#rootLogger.addHandler(consoleHandler)
#logging.root.setLevel(logging.INFO)
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['UPLOADED_PHOTOS_DEST'] = UPLOAD_FOLDER
photos = UploadSet('photos', ['pdf','png', 'jpeg','jpg','webp'])
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
    if not request_body and request.form:
        logging.info('Body: %s', str(request.form))    
        print('Body: %s', str(request.form))    
        if request.files:
            print('Request file: %s', str(request.files))    
    logging.info('Body: %s', json.dumps(request_body))
    print('Body: %s', json.dumps(request_body))

@app.after_request
def after_request_func(response):
    if type(response) == Response and response.get_json():
        response.set_data(json.dumps(handle_mongoengine_response(response.get_json())).encode("utf-8"))
    logging.info("Response is: "+json.dumps(response.get_json()))
    return response

@app.route("/which", methods=["GET"])
def root():
    server_number = app.config["PORT"]
    return "This is the superstore backend api %s server"%server_number


from routes import auth
from routes import category
from routes import product
from routes import user
from routes import order
from flask_session import Session

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
if not disable_socketio:
    import eventlet
    eventlet.monkey_patch()
    from flask_socketio import SocketIO

# socketio = SocketIO(logger=True,engineio_logger=True,cors_allowed_origins='*',message_queue='redis://127.0.0.1:6379')
    socketio = SocketIO(cors_allowed_origins='*', manage_session=False)
    socketio.init_app(app,message_queue='redis://')
    from events import events

    @socketio.on_error_default  # handles all namespaces without an explicit error handler
    def default_error_handler(e):
        print("SocketIO Error has occured: "+str(e))

    if __name__ == "__main__":
        socketio.run(app)


from routes import chat
app.register_blueprint(chat.bp)



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
    
