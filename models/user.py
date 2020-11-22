from werkzeug.security import check_password_hash, generate_password_hash as generate_password_hash_
from app import app
from utils.time import get_time_after
from datetime import datetime
import uuid

class User():

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash_(password)
        self.created_at = datetime.now()
        self.email_verified = False
        self.verification_token,self.verification_token_expiry = User.create_token()

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def create_token():
        return (str(uuid.uuid4()),get_time_after(minutes=0,hours=24))

    @staticmethod
    def generate_password_hash(password):
        return generate_password_hash_(password)

    def save(self):
        self.id = app.mongo.db.users.insert(self.__dict__)
        print(str(self.id))
        if self.id:
            return True
        else:
            return False