
from flask import request, jsonify
from models.user import Users
import json
from app import app
import bson
from bson import ObjectId
from utils.session import authorize
import traceback
from utils.aws import upload_image
from database.product import Get
from utils.response import create_failure_response, create_success_response
from database.user import Get as UserDb

@app.route("/user", methods=["GET"])
def get_user():
    response = {}
    payload = request.args
    user_id = payload.get("id")
    if not user_id:
        response["success"] = False
        response["message"] = "User id missing"
    else:
        try:
            db = UserDb()
            user = db.get_user_by_id(user_id)
            if not user:
                response["success"] = False
                response["message"] = "user not found"
            response = user
        except bson.errors.InvalidId:
            response["success"] = False
            response["message"] = "Improper user id passed"
    return jsonify(response)

@app.route("/logged_in_user", methods=["GET"])
@authorize
def get_logged_in_user(user_id, email):
    response = {}
    try:
        db = UserDb()
        user = db.get_user_by_id(user_id)
        if not user:
            response["success"] = False
            response["message"] = "user not found"
        response = user
    except bson.errors.InvalidId:
        response["success"] = False
        response["message"] = "Improper user id passed"
    return jsonify(response)

@app.route("/user", methods=["PATCH"])
@authorize
def updated_user(user_id,email):
    
    try:
        payload = request.get_json() if request.get_json() else request.form.to_dict()    
        # user_id = payload.pop("user_id")
        if request.method == 'PATCH' and 'document' in request.files:
            payload["document_url"] = upload_image(request.files['document'])
        updated_user = Users.objects.filter(id=ObjectId(user_id)).update(**payload)
        
        if updated_user:
            return create_success_response("User updated successfully")
        else:
            return create_failure_response("Something went wrong")
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

# [{
    #     "product_id":"",
    #     "quantity":,
    #     "price":
    # },
    # {
    #     "product_id":"",
    #     "quantity":,
    #     "price":
    # }]
@app.route("/add_to_cart", methods=["POST"])
@authorize
def add_product_to_cart(user_id, email):
    try:
        payload = request.get_json()
        input_quantity = None
        input_price = None
        if payload.get("quantity"):
            input_quantity = int(payload.get("quantity"))
        if payload.get("price"):
            input_price = float(payload.get("price"))
        product_id = payload.get("product_id","")
        if product_id:
            db = Get()
            product = db.get_product_by_id(product_id)
            seller_id = product.get("seller_id")
            if not product:
                return {"success":False, "message":"Invalid product details"}
            product_price = product.get("price")
            input_price = input_price if input_price else product_price
            user = json.loads(Users.objects(id=ObjectId(user_id)).first().to_json())
            
            user_cart = user.get("cart",[])
            # if len(user_cart) > 0:
            #     first_product_id = user_cart[0].get("product_id")
            #     first_product = db.get_product_by_id(first_product_id)
            #     first_seller_id = first_product.get("seller_id")
            #     # if first_seller_id != seller_id:
            #     #     return create_failure_response("Cart has products from a different seller! Clear the cart to add products from this seller.")
                
            if input_price < product_price:
                for cart in user_cart:
                    # we can add a secret key check to ensure that nobody can add things to cart with lesser product price without following the receipt workflow
                    if cart.get("price") and cart.get("price") < product_price and cart.get("product_id") == product_id:
                        return {"success":False, "message": "Cannot update cart with negotiated price"}
                user_cart.append({"price":input_price, "quantity": input_quantity, "product_id": product_id, "cart_type":"receipt"})
            elif input_price == product_price:
                cart_updated = False
                for i in range(len(user_cart)):
                    if user_cart[i].get("price") == input_price and user_cart[i].get("product_id") == product_id:
                        user_cart[i].update({"price":user_cart[i].get("price"),"quantity":user_cart[i].get("quantity")+1, "cart_type":"non_receipt"})
                        cart_updated = True
                if not cart_updated:
                    user_cart.append({"price":input_price if input_price else product.get("price"), "quantity": 1, "product_id": product_id, "cart_type":"non_receipt"})
            else:
                return {"success":False, "message":"Cart price cannot be greater than product price"}

            updated_user = Users.objects.filter(id=ObjectId(user_id)).update(**{"cart":user_cart})
            if updated_user:
                return {"success":True, "message":"Cart updated successfully"}
            else:
                return {"success":False, "message":"Something went wrong"}
        else:
            return {"success":False, "message":"Data missing in request"}
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

@app.route("/delete_from_cart", methods=["POST"])
@authorize
def delete_from_cart(user_id, email):
    try:
        payload = request.get_json()
        product_id = payload.get("product_id","")
        cart_type = payload.get("cart_type","")
        cart_found = False
        if product_id:
            db = Get()
            product = db.get_product_by_id(product_id)
            if not product:
                return {"success":False, "message":"Invalid product details"}
            user = json.loads(Users.objects(id=ObjectId(user_id)).first().to_json())
            user_cart = user.get("cart",[])
            for i in range(len(user_cart)):
                if user_cart[i].get("product_id") == product_id and user_cart[i].get("cart_type") == cart_type:
                    cart_found = True
                    if cart_type == "receipt":
                        del user_cart[i]
                        break
                    elif cart_type == "non_receipt":
                        quantity = user_cart[i].get("quantity")
                        updated_quantity = quantity - 1
                        if updated_quantity <= 0:
                            del user_cart[i]
                        else:
                            user_cart[i]["quantity"] = updated_quantity
                        break
                    else:
                        return create_failure_response("Invalid cart details")
            if not cart_found:
                return create_failure_response("Invalid cart details")
            updated_user = Users.objects.filter(id=ObjectId(user_id)).update(**{"cart":user_cart})
            if updated_user:
                return {"success":True, "message":"Cart updated successfully"}
            else:
                return {"success":False, "message":"Something went wrong"}
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")


@app.route("/add_receipt", methods=["POST"])
@authorize
def add_receipt_to_buyer(user_id, email):
    try:
        payload = request.get_json()
        required_fields = {"product_id", "quantity", "price", "buyer_id"}
        if set(payload.keys()).intersection(required_fields) != required_fields:
            return {"success":False, "message":"Data missing in request"}
        db = Get()
        product = db.get_product_by_id()
        if product.get("seller_id") != user_id:
            return {"success":False, "message":"You are not authorized to perform this operation"}
        new_receipt = dict((k, payload[k]) for k in required_fields)
        buyer_id = payload.get("buyer_id")
        user = json.loads(Users.objects(id=ObjectId(buyer_id)).first().to_json())
        buyer_receipts = user.get("receipts",[])

        if buyer_receipts and any(product_id in receipt.values() for receipt in receipts):
            for i in range(len(buyer_receipts)):
                if product_id == buyer_receipts[i].get("product_id"):
                    # quantity = buyer_receipts[i].get("quantity",0)+1
                    buyer_receipts[i].update(**new_receipt)
        else:
            buyer_receipts.append(**new_receipt)
                    
        updated_user = Users.objects.filter(id=ObjectId(buyer_id)).update(**{"receipts":buyer_receipts})
        if updated_user:
            return {"success":True, "message":"Receipt added to the user successfully"}
        else:
            return {"success":False, "message":"Something went wrong"}
            
    except:
        print(traceback.format_exc())
        return create_failure_response("Something went wrong")

@app.route("/cart", methods = ["GET"])
@authorize
def get_cart(user_id, email):
    db = UserDb()
    cart = db.get_cart_by_user_id(user_id)
    return jsonify(cart)