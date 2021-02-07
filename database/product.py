from mongoengine.base.fields import ObjectIdField
from utils._json import handle_mongoengine_json
from models.product import Products
from bson.objectid import ObjectId

class Get:
    def __init__(self):
        pass
    def get_product_by_id(self, product_id):
        product = Products.objects(id=ObjectId(product_id)).first().to_json()
        return handle_mongoengine_json(product)
    
        