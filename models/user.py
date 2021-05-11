from app import db
from werkzeug.security import check_password_hash, generate_password_hash as generate_password_hash_
from utils.time import get_time_after
from datetime import datetime
import uuid
from models.address import Address


class CartItem(db.EmbeddedDocument):
    product_id = db.StringField(required = True)
    price = db.FloatField(required = True)
    quantity = db.IntField()
    cart_type = db.StringField(required = True)

class Users(db.DynamicDocument):
    first_name = db.StringField(required = True)
    last_name = db.StringField(required = True)
    address = db.StringField()
    profile_pic = db.StringField()
    id_proof = db.StringField()
    is_id_verified = db.BooleanField()
    email = db.EmailField(required = True,unique =True)
    created_at = db.DateTimeField(required = True)
    email_verified = db.BooleanField(required=True)
    verification_token = db.StringField(required = True)
    verification_token_expiry = db.DateTimeField(required = True)
    password_hash = db.StringField(required = True)
    city = db.StringField(required = True)
    cart = db.ListField(db.EmbeddedDocumentField(CartItem))
    addresses = db.ListField(db.EmbeddedDocumentField(Address))


    @staticmethod
    def create_token():
        return (str(uuid.uuid4()),get_time_after(minutes=0,hours=24))

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def create_token():
        return (str(uuid.uuid4()),get_time_after(minutes=0,hours=24))

    @staticmethod
    def generate_password_hash(password):
        return generate_password_hash_(password)
    
    @staticmethod
    def create_user_data(payload):
        payload["password_hash"] = Users.generate_password_hash(payload["password"])
        del payload["password"]
        token,expiry = Users.create_token()
        payload["verification_token"] = token
        payload["verification_token_expiry"] = expiry
        payload["email_verified"] = False
        payload["created_at"] = datetime.now()
        return payload
