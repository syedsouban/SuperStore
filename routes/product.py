from datetime import datetime
import json
from flask.globals import session
import logging
from flask.templating import render_template
from models.chat import Chats
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
from utils.aws import upload_image
import traceback
import mongoengine
from utils._json import handle_mongoengine_response

import database

@app.route("/product", methods=["POST"])
@authorize
def create_product(user_id,email):
    # payload = request.get_json()
    payload = request.form.to_dict()
    if payload.get("tags"):
        payload["tags"] = payload["tags"].split(",")
    try:
        if request.method == 'POST' and 'photo' in request.files:
            payload["image_url"] = upload_image(request)        
        else:
            return {"success":False,"message":"Product image missing"}    
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

def search_products(filter_by, filter_by_value, sort_by, order, search_query):
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
    return products

def fetch_search_products_args(payload):
    filter_by = payload.get("filter_by")
    filter_by_value = payload.get("filter_by_value")
    sort_by = payload.get("sort_by")
    order = payload.get("order")
    search_query = payload.get("search_query")
    return filter_by, filter_by_value, sort_by, order, search_query

def fetch_products(payload):
    filter_by, filter_by_value, sort_by, order, search_query = fetch_search_products_args(payload)
    products = search_products(filter_by, filter_by_value, sort_by, order, search_query)
    return handle_mongoengine_response(products)

@app.route("/products", methods=["GET"])
def get_products():
    payload = request.args
    products = fetch_products(payload)
    return jsonify(products)

@app.route("/products_chat", methods=["GET"])
@authorize
def products_chat(user_id,email):
    payload = request.args

    print(request.host+" "+request.host_url+request.url+" "+request.url_root)
    # payload = request.get_json() if request.get_json() else {}
    filter_by = payload.get("filter_by")
    filter_by_value = payload.get("filter_by_value")
    sort_by = payload.get("sort_by")
    order = payload.get("order")
    search_query = payload.get("search_query")
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

    if payload.get("buy_first", False):
        product = products[0]
        product_id = product.get("_id").get("$oid")
        seller_id = product.get("seller_id").get("$oid")    
        buyer_id = str(user_id)
        return init_chat(email,buyer_id,seller_id,product_id)

    return jsonify(products)


# @authorize_web
@app.route('/list_products')
def list_products():
    try:
        user_id = session['user_id']
        email = session['email']
        html_res = "<html>"
        products = handle_mongoengine_response(search_products().get_json())
        for product in products:
            pname = product['english_name']
            pid = product['_id']
            url = url_for("chat.chat")
            # session['product_id'] = pid
            html_res+='<a href="%s">'%url+pname+"</a><br>"
        html_res += "</html>"
        return html_res
    except:
        import traceback
        print(traceback.format_exc())
    return ""

def init_chat(buyer_email,buyer_id,seller_id,product_id):
    product_chat = get_or_none(Chats.objects(Q(product_id=ObjectId(product_id)) & Q(seller_id=ObjectId(seller_id)) & Q(
        buyer_id=ObjectId(buyer_id))))
    payload = {
        "buyer_id":buyer_id,
        "seller_id":seller_id,
        "product_id":product_id
    }
    if not product_chat:
        try:
            product_chat = Chats(**payload).save()
            if not product_chat:
                print("Unable to save user chat")
                return {"status":False, "message":"Something went wrong"}
        except:
            print("Exception occured while saving chat: ")
            print(traceback.format_exc())
            return {"status":False, "message":"Something went wrong"}
    
    #create room with sid as combination of buyer_id, seller_id and product_id and add buyer to the room
    #whenever seller comes online add him to the room
    print(buyer_email,buyer_id,seller_id,product_id)
    room = str(product_id)+"_"+str(seller_id)+"_"+str(buyer_id)
    session['name'] = buyer_email
    session['room'] = room      

    return render_template('chat.html', name=buyer_id, room=room)


@app.route("/buy_product", methods=["GET"])
@authorize
def chat_product(user_id, email):
    payload = request.args
    product_id = None
    seller_id = None
    input_product_id = payload.get("product_id")
    if input_product_id:
        product_id = input_product_id
        db = database.product.Get()
        product_obj = db.get_product_by_id(product_id)
        if product_obj:
            seller_id = product_obj.get("seller_id")
    else:
        relevant_products = fetch_products(payload)
        if len(relevant_products) > 0:
            product_id = str(relevant_products[0].get("_id"))
            seller_id = relevant_products[0].get("seller_id")
        else:
            logging.root.info("Neither product is passed nor a product was found using params!")
    # logging.root.info()
    if not product_id or not seller_id:
        return "Cannot find product_id and/or seller_id"+"Product_id = "+str(product_id)+"Seller_id = "+str(seller_id)
    print(email, user_id,seller_id, product_id)
    return init_chat(email, user_id,seller_id, product_id)