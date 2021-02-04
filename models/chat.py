from mongoengine.queryset.base import CASCADE
from models.product import Products
from models.user import Users
from app import db

class Chats(db.DynamicDocument):
    product_id = db.LazyReferenceField(Products,required = True,dbref = False,reverse_delete_rule = CASCADE)
    seller_id = db.LazyReferenceField(Users,required = True,dbref = False,reverse_delete_rule = CASCADE)
    buyer_id = db.LazyReferenceField(Users,required = True,dbref = False,reverse_delete_rule = CASCADE)
    
    
    