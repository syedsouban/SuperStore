from app import db
from werkzeug.security import check_password_hash, generate_password_hash as generate_password_hash_
from utils.time import get_time_after
from datetime import datetime
import uuid

class Users(db.DynamicDocument):
    
    email = db.EmailField(required = True,unique =True)
    created_at = db.DateTimeField(required = True)
    email_verified = db.BooleanField(required=True)
    verification_token = db.StringField(required = True)
    verification_token_expiry = db.DateTimeField(required = True)
    password_hash = db.StringField(required = True)

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
