from app import db

class Address(db.EmbeddedDocument):
    is_primary = db.BooleanField()
    city = db.StringField(required = True)
    state = db.StringField(required = True)
    country = db.StringField(required = True)
    street_address = db.StringField(required = True)