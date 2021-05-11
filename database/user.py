from mongoengine.base.fields import ObjectIdField
from utils._json import handle_mongoengine_json
from bson.objectid import ObjectId
import json
from utils.response import create_failure_response
from flask import abort
from database.product import Get as ProductDb
from models.user import Users

class Get:
    def __init__(self):
        pass
    def get_user_by_id(self, user_id):
        user = Users.objects(id=ObjectId(user_id)).first()
        if not user:
            abort(500,create_failure_response("Invalid input payload"))
            logging.info("User with id %s does not exist"%user_id)
        response = json.loads(user.to_json())
        
        cart = response.get("cart")
        for i in range(len(cart)):
            db = ProductDb()
            product_id = cart[i].get("product_id")
            price = cart[i].get("price")
            product = db.get_product_by_id(product_id, False)
            if price:
                product.pop("price")
            cart[i].update(product)
        print(str(cart)+"\n\n\n"+str(type(cart)))
        response.update({"cart":cart})
        response.pop("password_hash")
        response.pop("verification_token")
        print("====================>"+json.dumps(response))
        return handle_mongoengine_json(response)
    
    def get_cart_by_user_id(self, user_id):
        user = Users.objects(id=ObjectId(user_id)).first()
        if not user:
            abort(500,create_failure_response("Invalid input payload"))
            logging.info("User with id %s does not exist"%user_id)
        response = json.loads(user.to_json())
        cart = response.get("cart")
        return cart
    
        