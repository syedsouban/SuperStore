import json
from bson import json_util
from bson.objectid import ObjectId
from routes.auth import authorize
import pymongo
from app import app
from flask import request
from flask import request,jsonify
from constants import fields
import traceback
from flask_pymongo import PyMongo

@app.route("/product", methods=["POST"])
@authorize
def create_product(user_id,email):
    payload = request.get_json()
    try:
        if payload.get("seller_id") and payload.get("category_id"):
            payload["seller_id"] = ObjectId(payload["seller_id"])
            payload["category_id"] = ObjectId(payload["category_id"])
        inserted = app.mongo.db.products.insert(payload)
        if inserted:
            return {"success":True,"message":"Product created successfully"}
        else:
            return {"success":False,"message":"Something went wrong"}
    except pymongo.errors.WriteError:
        print(traceback.format_exc())
        return {"success":False,"message":"Some or all the fields were not present"}
    except:
        return {"success":False,"message":"Something went wrong"}

@app.route("/products", methods=["GET"])
@authorize
def get_products(user_id,email):
    db = PyMongo(app).db
    products = db.products.find()
    products = json.loads(json_util.dumps(products))
    return jsonify(products)
    