from models import Address

class Orders(db.DynamicDocument):
    order_id = db.StringField(required = True)
    payment_details = db.StringField(required = True)
    delivery_address = db.StringField(required = True)
    buyer_id = db.StringField(required = True)
    seller_id = db.StringField(required = True)
    cart = db.ListField(db.EmbeddedDocumentField(CartItem))
    address = db.EmbeddedDocumentField(Address, required = True)
    status = db.StringField(required = True)
    