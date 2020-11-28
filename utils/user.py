from bson import ObjectId

from datetime import datetime
from constants import fields

def get_verified_users_by_id(user_id):
    return app.mongo.db.users.find_one({"$and": [
                {
                    fields._id: {
                        "$eq": ObjectId(user_id)
                    }
                },
                {
                    fields.email_verified: {
                        "$eq": True
                    }
                }
            ]
        })

def update_token(token_type,user_id,token,token_expiry):
    return app.mongo.db.users.update(
            {"_id": user_id},
            {

                "$set": {
                    token_type: token,
                    token_type+"_expiry": token_expiry
                }
            }
            )

def get_users_by_token_and_email(token_type,token,email):
    return app.mongo.db.users.find_one({"$and": [
                {
                    token_type: {
                        "$eq": token
                    }
                },
                {
                    token_type+"_expiry": {
                        "$gte": datetime.now()
                    }
                },
                {
                    fields.email: {
                        "$eq": email
                    }
                }
            ]
        })

def update_email_verify_status(email):
    return app.mongo.db.users.update(
            {fields.email: email},
            {

                "$set": {
                    fields.email_verified: True
                }
            }
            )

def get_user_by_email(email):
    return app.mongo.db.users.find_one({"$and": [
                
                {
                    fields.email: {
                        "$eq": email
                    }
                }
            ]
        })

def update_password_by_id(user_id,new_password_hash):
    return app.mongo.db.users.update(
                                    {fields._id: ObjectId(user_id)},
                                    {
                                        "$set": {
                                            fields.password_hash: new_password_hash,
                                            fields.password_token_expiry: datetime.now()
                                        }
                                    }
                                    )
from app import app