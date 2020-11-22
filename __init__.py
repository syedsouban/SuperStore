from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["SECRET_KEY"] = "5d8b7997-de22-49a0-b76f-87da47d5b2ab"
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/superStoreDb"
app.mongo = PyMongo(app)
app.APP_URL = "http://127.0.0.1:5000"

if __name__ == "__main__":
    app.run(debug=True)

from routes import auth
