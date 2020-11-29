from app import db

class Categories(db.DynamicDocument):
    english_name = db.StringField()
    arabic_name = db.StringField(required=True)
    english_tagline = db.StringField(required=True)
    arabic_tagline = db.StringField(required=True)
    english_description = db.StringField(required=True)
    arabic_description = db.StringField(required=True)
    image_url = db.URLField(required=True)
    discount = db.FloatField(required=True)