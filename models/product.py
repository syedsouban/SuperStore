from mongoengine.fields import StringField
from mongoengine.queryset.base import CASCADE
from models.category import Categories
from models.user import Users
from app import db

class Products(db.DynamicDocument):
    english_name = db.StringField(unique = True)
    arabic_name = db.StringField(required=True)
    english_description = db.StringField(required=True)
    arabic_description = db.StringField(required=True)
    image_url = db.URLField(required=True)
    category_id = db.LazyReferenceField(Categories,required = True,dbref = False,reverse_delete_rule = CASCADE)
    seller_id = db.LazyReferenceField(Users,required = True,dbref = False,reverse_delete_rule = CASCADE)
    price = db.FloatField(required=True)
    discount = db.FloatField(required=True)
    FAQs_arabic = db.ListField()
    FAQs_english = db.ListField()
    tags = db.ListField(required = True)
    status = db.StringField(required = True)
    created_date = db.DateTimeField()
    updated_date = db.DateTimeField()

    meta = {'indexes': [
        {'fields': ['$english_name', "$english_description", "$tag"],
         'default_language': 'english',
         'weights': {'english_name': 15, 'tags': 10, 'description': 5}
        }
    ]}
    
    