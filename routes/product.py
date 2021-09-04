from datetime import datetime
import json
from flask.globals import session
import logging
from flask.templating import render_template
from mongoengine.queryset.transform import query
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
from utils.response import create_failure_response, create_success_response

from database import product

@app.route("/product", methods=["POST"])
@authorize
def create_product(user_id,email):
    # payload = request.get_json()
    payload = request.form.to_dict()
    is_arabic_image_same = bool(payload.get("is_arabic_image_same", False))
    if payload.get("tags"):
        payload["tags"] = payload["tags"].split(",")
    try:
        if request.method == 'POST' and ('english_images[]' in request.files):
            english_images = request.files.getlist("english_images[]")
            arabic_images = request.files.getlist("arabic_images[]")
            print(str(english_images)+" "+str(arabic_images))
            
            arabic_image_urls = []
            english_image_urls = []
            if not is_arabic_image_same:
                for image in arabic_images:
                    url = upload_image(image)
                    if url:
                        arabic_image_urls.append(url)
            
            for image in english_images:
                url = upload_image(image)
                if url:
                    english_image_urls.append(url)
            payload["arabic_image_urls"] = english_image_urls if is_arabic_image_same else arabic_image_urls
            payload["english_image_urls"] = english_image_urls
            payload["image_url"] = english_image_urls[0] if len(english_image_urls) > 0 else None
        else:
            return create_failure_response("Product image missing")    
        payload["seller_id"] = ObjectId(user_id)
        payload["status"] = "pending"
        if payload.get("category_id"):
            payload["category_id"] = ObjectId(payload["category_id"])
        payload = create_who_columns(email=email,payload=payload)
        inserted = Products(**payload).save()
        if inserted:
            return {"success":True,"message":"Product created successfully","product_id":str(inserted.id)}
        else:
            return create_failure_response("Something went wrong")
    except pymongo.errors.WriteError:
        print(traceback.format_exc())
        return create_failure_response("Some or all the fields were not present")
    except mongoengine.errors.NotUniqueError:
        print(traceback.format_exc())
        return create_failure_response("Product with the same name already exists")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

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
        status = payload.get("status")
        if status and status in ["pending", "approved", "rejected"]:
            new_product["status"] = status
        updated_product = Products.objects.filter(id=ObjectId(product_id)).update(**new_product)
        
        if updated_product:
            return create_success_response("Product updated successfully")
        else:
            return create_failure_response("Something went wrong")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

@app.route("/product", methods=["DELETE"])
@authorize
def delete_product(user_id,email):
    payload = request.get_json()
    try:
        product_id = payload.pop("product_id")
        # document = create_fields_for_deletion(email)
        # updated_category = Categories.objects.filter(id=ObjectId(category_id)).update(**document)
        deleted_product = Products.objects(id=ObjectId(product_id)).delete()
        if deleted_product >=1:
            return create_success_response("Product deleted successfully")
        else:
            return create_failure_response("Something went wrong")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

def search_products(filter_by, filter_by_value, sort_by, order, search_query, debug = False):
    if order and sort_by:
        if order == 'asc':
            sort_by = '+'+sort_by
        elif order == 'desc':
            sort_by = '-'+sort_by
        else:
            print("Improper sort order sent")
    else:
        sort_by = 'created_at'
    
    query_dict = {"status":"approved"} if not debug else {}
    
    if filter_by and filter_by_value:
        if 'category' in filter_by:
            category_id = get_or_none(Categories.objects(**{filter_by.replace('category_',''):filter_by_value})).id
            if category_id:
                category_id = ObjectId(category_id)
                query_dict.update({"category_id":category_id})
                queries = Q(**query_dict)
                if not search_query:
                    products = Products.objects(queries).order_by(sort_by).to_json()    
                else:
                    products = Products.objects(queries).search_text(search_query).order_by(sort_by).to_json()
            else:
                return []
        else:
            query_dict.update({filter_by:filter_by_value})
            products = Products.objects(**query_dict).to_json()
    else:
        if not search_query:
            products = Products.objects(Q(**query_dict)).order_by(sort_by).to_json()
        else:
            products = Products.objects(Q(**query_dict)).search_text(search_query).order_by(sort_by).to_json()
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
    products = search_products(filter_by, filter_by_value, sort_by, order, search_query, debug = payload.get("debug"))
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
    print("payload"+json.dumps(payload))
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
        if 'category' in filter_by:
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
            products = Products.objects(**{filter_by:filter_by_value})
    else:
        if not search_query:
            products = Products.objects().order_by(sort_by).to_json()
        else:
            products = Products.objects().search_text(search_query).order_by(sort_by).to_json()
    products = json.loads(products)

    return jsonify(products)



@app.route('/list_products')
@authorize
def list_products(user_id, email):
    try:
        # user_id = session['user_id']
        # email = session['email']
        html_res = "<html>"
        products = handle_mongoengine_response(search_products(None, None, None, None, None))
        for product in products:
            pname = product['english_name']
            pid = product['_id']
            # url = url_for("chat.chat")
            # session['product_id'] = pid
            seller_id = product.get("seller_id")
            print("user_id = ",user_id," seller_id = ",seller_id,user_id==seller_id,type(user_id),type(seller_id))
            
            if str(user_id)!=seller_id:
                html_res+='<a href="init_chat?product_id=%s">'%pid+pname+"</a><br>"
        html_res += "</html>"
        return html_res
    except:
        import traceback
        print(traceback.format_exc())
    return ""

def init_chat(buyer_email,seller_email, buyer_id,seller_id,product_id, product_name):
    product_chat = get_or_none(Chats.objects(Q(product_id=ObjectId(product_id)) & Q(seller_id=ObjectId(seller_id)) & Q(
        buyer_id=ObjectId(buyer_id))))
    payload = {
        "buyer_id":buyer_id,
        "seller_id":seller_id,
        "product_id":product_id,
        "buyer_email":buyer_email,
        "seller_name":seller_email,
        "product_name":product_name
    }
    if product_chat:
        chat_id = product_chat.id
        print("chatid = chat_id")
    else:
        try:
            product_chat = Chats(**payload).save()
            chat_id = product_chat.id
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
    # send user_id, chat_id in response for mobile
    # session['name'] = buyer_email
    # session['user_id'] = buyer_id
    # session['room'] = room      
    # session_id = session.get("SESSION-ID")
    # print("session id fetched is: ",session_id)
    return jsonify({"chat_id":str(chat_id)})
    # return render_template('chat.html', name=buyer_email,buyer_id = buyer_id, room=room, session_id =session_id, buyer_email = buyer_email,seller_email = seller_email, product_name = product_name, chat_id = chat_id)


@app.route("/init_chat", methods=["GET"])
@authorize
def chat_product(user_id, email):
    payload = request.args
    product_id = None
    seller_id = None
    input_product_id = payload.get("product_id")
    buyer_email = email
    seller_email = None
    product_name = None
    if input_product_id:
        product_id = input_product_id
        db = product.Get()
        product_obj = db.get_product_by_id(product_id)
        if product_obj:
            seller_id = product_obj.get("seller_id")
            seller_email = product_obj.get("seller_email")
            product_name = product_obj.get("english_name")
    # logging.root.info()
    if not product_id or not seller_id or not buyer_email or not product_name:
        return "Cannot find product_id and/or seller_id"+"Product_id = "+str(product_id)+"Seller_id = "+str(seller_id)
    print(email, user_id,seller_id, product_id)
    return init_chat(buyer_email, seller_email, user_id,seller_id, product_id, product_name)