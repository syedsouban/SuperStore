from datetime import datetime
from app import app
from utils.time import get_time_after
import uuid
from constants import fields
from functools import wraps
from flask import abort,request
import logging

def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):
            logging.info("request headers are: "+str(request.headers))
            session_id_field = None
            if request.headers.get(fields.SESSION_ID):
                session_id_field = fields.session_id
            elif request.headers.get("SESSION_ID"):
                session_id_field = "SESSION_ID"
            if not session_id_field in request.headers:
               abort(401)
            try:
                session_id = request.headers.get(session_id_field)
                user_session = get_active_session_by_id(session_id)
                if not user_session:
                    abort(401)
            except:
                abort(401)

            return f(user_session[fields.user_id],user_session[fields.email], *args, **kws)
    return decorated_function



def update_session_id(session_id):
    return app.mongo.db.user_sessions.update(
            {fields.session_id: session_id},
            {

                "$set": {
                    fields.is_active: False,
                    fields.expireAt: get_time_after(days = 15)
                }
            }
    )

def get_active_sessions_by_user_id(user_id):
    return app.mongo.db.user_sessions.count_documents(
        {
            "$and": [
                {
                    fields.user_id: {
                        "$eq": user_id
                    }
                },
                {
                    fields.expiry_date: {
                        "$gte": datetime.today()
                    }
                },
                {
                    fields.is_active: {
                        "$eq": True
                    }
                }
            ]
        }
    )

def get_active_session_by_id(session_id):
    userFromSession = app.mongo.db.user_sessions.find_one({"$and": [
                {
                    fields.session_id: {
                        "$eq": session_id
                    }
                },
                {
                    fields.expiry_date: {
                        "$gte": datetime.today()
                    }
                },
                {
                    fields.is_active: {
                        "$eq": True
                    }
                }
            ]
        })
    return userFromSession

def create_new_session(user_id,email):
    session_id = str(uuid.uuid4())
    user_session = {
        fields.user_id: user_id,
        fields.session_id: session_id,
        fields.expiry_date: get_time_after(hours=12, minutes=0),
        fields.email:email,
        fields.is_active:True
    }
    return user_session if app.mongo.db.user_sessions.insert(user_session) else None
