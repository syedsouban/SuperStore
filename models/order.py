from models.user import Users
from models.address import Address
from app import db

class Orders(db.DynamicDocument):
    payment_type = db.StringField(required = True)
    payment_details = db.StringField(required = True)
    buyer_id = db.LazyReferenceField(Users, required = True)
    seller_id = db.LazyReferenceField(Users, required = True)
    quantity = db.FloatField(required = True)
    price = db.FloatField(required = True)
    status = db.StringField(required = True)
    address = db.EmbeddedDocumentField(Address, required = True)
    status = db.StringField(required = True)
    