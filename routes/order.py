from datetime import datetime
import json
import traceback
from utils.misc import get_update_dict
from utils.response import create_failure_response, create_success_response
import bson
from bson.objectid import ObjectId
from flask.json import jsonify
from models.user import Users
from models.order import Orders
from app import app
from flask import request
from utils.session import authorize
from database.user import Get as UserDb
from database.order import Get as OrderDb
from database.product import Get as ProductDb
from routes.user import updated_user

@app.route("/order", methods=["GET"])
def get_order():
    response = {}
    payload = request.args
    order_id = payload.get("id")
    if not order_id:
        response["success"] = False
        response["message"] = "Order id missing"
    else:
        try:
            db = OrderDb()
            order = db.get_order_by_id(order_id)
            if not order:
                response["success"] = False
                response["message"] = "order not found"
            response = order
        except bson.errors.InvalidId:
            response["success"] = False
            response["message"] = "Improper order id passed"
    return jsonify(response)

@app.route("/buying_orders", methods=["GET"])
@authorize
def get_orders(user_id, email):
    orders = (Orders.objects(buyer_id=user_id).to_json())
    orders = json.loads(orders)
    return jsonify(orders)

@app.route("/selling_orders", methods=["GET"])
@authorize
def get_selling_orders(user_id, email):
    orders = (Orders.objects(seller_id=user_id).to_json())
    orders = json.loads(orders)
    return jsonify(orders)

@app.route("/checkout", methods=["POST"])
@authorize
def checkout(user_id, email):
    payload = request.get_json()
    payment_type = payload.get("payment_type")
    payment_details = payload.get("payment_details")
    address = payload.get("address")
    db = UserDb()
    productDb = ProductDb()
    cart = db.get_cart_by_user_id(user_id)
    if len(cart) == 0:
        return {"status":True,"message":"Cart is empty"}
    for item in cart:
        print("item: "+str(item))
        product_id = item.get("product_id")
        product = productDb.get_product_by_id(product_id=product_id)
        seller_id = product.get("seller_id")
        cart_type = item.get("cart_type")
        quantity = item.get("quantity")
        price = item.get("price")
        status = "P"
        inserted = Orders(product_id = product_id, payment_type = payment_type, address = address,
        payment_details = payment_details, cart_type = cart_type, quantity = quantity,
        price = price, seller_id = seller_id, buyer_id = str(user_id), status = status).save()
        if not inserted:
            return {"status":False, "message":"Something went wrong"}
        updated_user = Users.objects.filter(id=ObjectId(user_id)).update(**{"cart":[]})
    
    return {"status":True, "message":"Order created successfully!"}

@app.route("/order", methods=["PATCH"])
@authorize
def update_order(user_id,email):
    payload = request.get_json()
    try:
        order_id = payload.pop("order_id")
        new_order = {}
        new_order["updated_by"] = email
        new_order["updated_date"] = datetime.now()
        status = payload.get("status")
        if status and status in ["Placed", "Shipped", "Delivered"]:
            new_order["status"] = status
        updated_order = Orders.objects.filter(id=ObjectId(order_id)).update(**new_order)
        
        if updated_order:
            return create_success_response("order updated successfully")
        else:
            return create_failure_response("Something went wrong")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")
    