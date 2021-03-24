from mongoengine.queryset.base import CASCADE
from models.chat import Chats
from models.user import Users
from app import db

class Messages(db.DynamicDocument):
    chat_id = db.LazyReferenceField(Chats, required = True,dbref = False,reverse_delete_rule = CASCADE)
    receipt = db.DictField()
    text = db.StringField()
    message_type = db.StringField(required = True)
    author_id = db.LazyReferenceField(Users, required = True,dbref = False,reverse_delete_rule = CASCADE)
    timestamp = db.DateTimeField()