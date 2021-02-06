from utils._json import handle_mongoengine_json

class Get:
    def __init__(self):
        pass
    def get_product_by_id(product_id):
        product = Products.objects(id=ObjectId(product_id)).first()
        return handle_mongoengine_json(product)
    
        