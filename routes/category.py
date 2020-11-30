# CRUD for category
from datetime import datetime
import json

from bson.objectid import ObjectId
from utils.misc import create_fields_for_deletion, create_who_columns, get_update_dict
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
        payload["is_active"] = True
        payload["seller_id"] = user_id
        payload = create_who_columns(email=email,payload=payload)
        inserted_category = Categories(**payload).save()
        if inserted_category:
            return {"success":True,"message":"Catgeory create successfully","category_id":str(inserted_category.id)}
        else:
            return {"success":False,"message":"Something went wrong"}
    except pymongo.errors.WriteError:
        print(traceback.format_exc())
        return {"success":False,"message":"Category already exists or some fields are missing"}
    except:
        print(traceback.format_exc())
        return {"success":False,"message":"Something went wrong"}

@app.route("/categories", methods=["GET"])
@authorize
def get_categories(user_id,email):
    categories = Categories.objects(is_active=True).to_json()
    categories = json.loads(categories)    
    return jsonify(categories)


@app.route("/category", methods=["PATCH"])
@authorize
def updated_category(user_id,email):
    payload = request.get_json()
    try:
        category_id = payload.pop("category_id")
        new_category = get_update_dict(payload)
        new_category["updated_by"] = email
        new_category["updated_date"] = datetime.now()
        updated_category = Categories.objects.filter(id=ObjectId(category_id)).update(**new_category)

        if updated_category:
            return {"success":True,"message":"Catgeory updated successfully"}
        else:
            return {"success":False,"message":"Something went wrong"}
    except:
        print(traceback.format_exc())
        return {"success":False,"message":"Something went wrong"}

@app.route("/category", methods=["DELETE"])
@authorize
def delete_category(user_id,email):
    payload = request.get_json()
    try:
        category_id = payload.pop("category_id")
        document = create_fields_for_deletion(email)
        # updated_category = Categories.objects.filter(id=ObjectId(category_id)).update(**document)
        deleted_category = Categories.objects(id=ObjectId(category_id)).delete()
        if deleted_category >=1 :
            return {"success":True,"message":"Catgeory deleted successfully"}
        else:
            return {"success":False,"message":"Something went wrong"}
    except:
        print(traceback.format_exc())
        return {"success":False,"message":"Something went wrong"}