from utils.misc import get_or_none
from utils.time import get_time_after
from constants import fields
from models.user import Users
import uuid
from app import db
class UserSessions(db.DynamicDocument):
    user_id = db.LazyReferenceField(Users,required = True,dbref = False)
    session_id = db.StringField(required = True)
    is_active = db.BooleanField(required=True)
    expiry_date = db.DateTimeField(required = True)

    @staticmethod
    def create_new_session(user_id,email):
        
        session_id = str(uuid.uuid4())
        user_session = {
            fields.user_id: user_id,
            fields.session_id: session_id,
            fields.expiry_date: get_time_after(days = 30, hours=0, minutes=0),
            fields.email:email,    
            fields.is_active:True
        }
        new_session = UserSessions(**user_session).save()
        return new_session    
    
