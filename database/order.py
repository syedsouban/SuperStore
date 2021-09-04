from utils._json import handle_mongoengine_json
from models.order import Orders
from bson.objectid import ObjectId
import json

class Get:
    def __init__(self):
        pass
    def get_order_by_id(self, order_id):
        order = Orders.objects(id=ObjectId(order_id)).first()
        order_json = json.loads(order.to_json())
        return handle_mongoengine_json(order_json)