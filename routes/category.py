# CRUD for category
from datetime import datetime
import json

import bson
from bson.objectid import ObjectId
from utils.misc import create_fields_for_deletion, create_who_columns, get_update_dict

import pymongo

from flask import request
from flask import request,jsonify
import traceback
from models.category import Categories
from utils.session import authorize
from app import app
from utils.aws import upload_image
from utils.response import create_failure_response, create_success_response, get_default_response

@app.route("/category", methods=["POST"])
@authorize
def create_category(user_id,email):
    # payload = request.get_json()
    payload = request.form.to_dict()
    if payload.get("tags"):
        payload["tags"] = payload["tags"].split(",")
    try:
        payload["is_active"] = True
        if request.method == 'POST' and 'photo' in request.files:
            payload["image_url"] = upload_image(request.files['photo'])        
        else:
            return create_failure_response("Category image missing")
        payload["seller_id"] = user_id
        payload = create_who_columns(email=email,payload=payload)
        inserted_category = Categories(**payload).save()
        if inserted_category:
            # pass category id in future
            #,"category_id":str(inserted_category.id)
            return create_success_response("Category created successfully")
        else:
            return create_failure_response("Something went wrong")
    except pymongo.errors.WriteError:
        print(traceback.format_exc())
        return create_failure_response("Category already exists or some fields are missing")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

@app.route("/categories", methods=["GET"])
def get_categories():
    categories = (Categories.objects(is_active=True).to_json())
    categories = json.loads(categories)
    return jsonify(categories)

@app.route("/category", methods=["GET"])
def get_category():
    response = get_default_response()
    payload = request.args
    product_id = payload.get("id")
    if not product_id:
        return create_failure_response("Category id missing")
    else:
        try:
            product = Categories.objects(id=ObjectId(product_id)).first()
            if product:
                response = json.loads(product.to_json())
            else:
                return create_failure_response("Category not found")
        except bson.errors.InvalidId:
            return create_failure_response("Improper category id passed")
    return jsonify(response)


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
            return create_success_response("Catgeory updated successfully")
        else:
            return create_failure_response("Something went wrong")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

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
            return create_success_response("Catgeory deleted successfully")
        else:
            return create_failure_response("Something went wrong")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")