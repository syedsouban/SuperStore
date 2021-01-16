from datetime import datetime
import json
from models.category import Categories
import bson
from mongoengine.queryset.visitor import Q
from utils.misc import create_who_columns, get_or_none, get_update_dict
from bson.objectid import ObjectId
from routes.auth import authorize
import pymongo
from app import app
from flask import request
from flask import request,jsonify
from models.product import Products
import traceback
import mongoengine

@app.route("/product", methods=["POST"])
@authorize
def create_product(user_id,email):
    payload = request.get_json()
    try:
        payload["seller_id"] = ObjectId(user_id)
        if payload.get("category_id"):
            payload["category_id"] = ObjectId(payload["category_id"])
        payload = create_who_columns(email=email,payload=payload)
        inserted = Products(**payload).save()
        if inserted:
            return {"success":True,"message":"Product created successfully","product_id":str(inserted.id)}
        else:
            return {"success":False,"message":"Something went wrong"}
    except pymongo.errors.WriteError:
        print(traceback.format_exc())
        return {"success":False,"message":"Some or all the fields were not present"}
    except mongoengine.errors.NotUniqueError:
        print(traceback.format_exc())
        return {"success":False,"message":"Product with the same name already exists"}
    except:
        print(traceback.format_exc())
        return {"success":False,"message":"Something went wrong"}

@app.route("/product", methods=["GET"])
def get_product():
    response = {}
    payload = request.args
    product_id = payload.get("id")
    if not product_id:
        response["success"] = False
        response["message"] = "Product id missing"
    else:
        try:
            product = Products.objects(id=ObjectId(product_id)).first()
            if product:
                response = json.loads(product.to_json())
            else:
                response["success"] = False
                response["message"] = "Product not found"
        except bson.errors.InvalidId:
            response["success"] = False
            response["message"] = "Improper product id passed"
    return jsonify(response)

@app.route("/products", methods=["GET"])
def get_products():
    payload = request.args
    # payload = request.get_json() if request.get_json() else {}
    filter_by = payload.get("filter_by")
    filter_by_value = payload.get("filter_by_value")
    sort_by = payload.get("sort_by")
    order = payload.get("order")
    search_query = payload.get("search_query")
    return search_products(search_query,filter_by,filter_by_value,sort_by,order)

def search_products(search_query = None,filter_by = None,filter_by_value = None,sort_by = None,order = None):
    if order and sort_by:
        if order == 'asc':
            sort_by = '+'+sort_by
        elif order == 'desc':
            sort_by = '-'+sort_by
        else:
            print("Improper sort order sent")
    else:
        sort_by = 'created_at'
    if filter_by and filter_by_value:
        category_id = get_or_none(Categories.objects(**{filter_by.replace('category_',''):filter_by_value})).id
        if category_id:
            category_id = ObjectId(category_id)
            queries = Q(**{"category_id":category_id})
            if not search_query:
                products = Products.objects(queries).order_by(sort_by).to_json()    
            else:
                products = Products.objects(queries).search_text(search_query).order_by(sort_by).to_json()
        else:
            return []
    else:
        if not search_query:
            products = Products.objects().order_by(sort_by).to_json()
        else:
            products = Products.objects().search_text(search_query).order_by(sort_by).to_json()
    products = json.loads(products)
    return jsonify(products)

@app.route("/product", methods=["PATCH"])
@authorize
def update_product(user_id,email):
    payload = request.get_json()
    try:
        product_id = payload.pop("product_id")
        new_product = get_update_dict(payload)
        new_product["updated_by"] = email
        new_product["updated_date"] = datetime.now()
        updated_product = Products.objects.filter(id=ObjectId(product_id)).update(**new_product)

        if updated_product:
            return {"success":True,"message":"Product updated successfully"}
        else:
            return {"success":False,"message":"Something went wrong"}
    except:
        print(traceback.format_exc())
        return {"success":False,"message":"Something went wrong"}

@app.route("/product", methods=["DELETE"])
@authorize
def delete_product(user_id,email):
    payload = request.get_json()
    try:
        product_id = payload.pop("product_id")
        # document = create_fields_for_deletion(email)
        # updated_category = Categories.objects.filter(id=ObjectId(category_id)).update(**document)
        deleted_product = Products.objects(id=ObjectId(product_id)).delete()
        if deleted_product >=1 :
            return {"success":True,"message":"Product deleted successfully"}
        else:
            return {"success":False,"message":"Something went wrong"}
    except:
        print(traceback.format_exc())
        return {"success":False,"message":"Something went wrong"}
