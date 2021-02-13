from mongoengine.base.fields import ObjectIdField
from utils._json import handle_mongoengine_json
from models.product import Products
from bson.objectid import ObjectId
import json

class Get:
    def __init__(self):
        pass
    def get_product_by_id(self, product_id):
        product = Products.objects(id=ObjectId(product_id)).first()
        print("product: "+str(product.to_json()))
        seller_obj = product.seller_id.fetch()
        product_json = json.loads(product.to_json())
        product_json.update({"seller_email":seller_obj.email})
        return handle_mongoengine_json(product_json)
    
        