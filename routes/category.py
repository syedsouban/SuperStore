# CRUD for category
from email import message
import json
from bson import json_util
from routes.auth import authorize
import pymongo
from app import app
from flask import request
from flask import request,jsonify
import traceback
from models.category import Categories

@app.route("/category", methods=["POST"])
@authorize
def create_category(user_id,email):
    payload = request.get_json()
    try:
        inserted_category = Categories(**payload).save()
        if inserted_category:
            return {"success":True,"message":"Catgeory create successfully"}
        else:
            return {"success":False,"message":"Something went wrong"}
    except pymongo.errors.WriteError:
        print(traceback.format_exc())
        return {"success":False,"message":"Some or all the fields were not present"}
    except:
        print(traceback.format_exc())
        return {"success":False,"message":"Something went wrong"}

@app.route("/categories", methods=["GET"])
@authorize
def get_categories(user_id,email):
    categories = Categories.objects().all().values_list('id')
    categories = json.loads(json_util.dumps(categories))
    return jsonify(categories)
    