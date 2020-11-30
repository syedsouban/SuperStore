from enum import unique

from mongoengine.fields import DateTimeField
from app import db

class Categories(db.DynamicDocument):
    english_name = db.StringField(unique = True)
    arabic_name = db.StringField(required=True)
    english_tagline = db.StringField(required=True)
    arabic_tagline = db.StringField(required=True)
    english_description = db.StringField(required=True)
    arabic_description = db.StringField(required=True)
    image_url = db.URLField(required=True)
    discount = db.FloatField(required=True)
    meta = {
        'indexes': [
            {
                'name': 'TTL_index',
                'fields': ['expireAt'],
                'expireAfterSeconds': 0,
                
            }
        ]
    }
    expireAt = db.DateTimeField()
    created_date = db.DateTimeField()
    updated_date = db.DateTimeField()