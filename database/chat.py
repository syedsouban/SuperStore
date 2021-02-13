from utils._json import handle_mongoengine_json_array, handle_mongoengine_json
from models.chat import Chats
from models.message import Messages
from bson.objectid import ObjectId
from bson import json_util
from utils._json import is_json
import json
import datetime

class Get:
    def __init__(self):
        pass
    
    def get_user_field(self, chat_obj, prefix, field):
        return getattr(chat_obj, prefix+"_"+field)
     
    def get_user_antonyms(self,user_type):
        if user_type == "buyer":
            return "seller"
        elif user_type == "seller":
            return "buyer"
        else:
            raise Exception("Invalid user type")

    def get_chats_by_buyer_id_seller_id(self, user_id, user_type, fetch_latest_message = True, fetch_num_of_new_msgs = True):
        chats = Chats.objects(__raw__ = {user_type+"_id": ObjectId(user_id)})
        antonym_user_type = self.get_user_antonyms(user_type)
        chats_list = []
        for i in range(len(chats)):
            if is_json(chats[i].to_json()):
                user_obj = self.get_user_field(chats[i], antonym_user_type, "id").fetch()
                chat_obj = json.loads(chats[i].to_json())
                chat_id = str(chats[i].id)
                if fetch_latest_message:
                    pipeline = [{"$match":{ "chat_id": ObjectId(chat_id) }},
                    {"$sort":{"timestamp":-1}},
                    {"$group":{"_id":"$chat_id","messages":{"$push":"$$ROOT"}}},
                    {"$project":{"messages":{"$slice":["$messages", 1]}}}]
                    agg_obj = list(Messages.objects().aggregate(pipeline))
                    print(str(agg_obj))
                    latest_message = agg_obj[0].get("messages",[]) if len(agg_obj) > 0 else []
                    latest_message = latest_message[0] if len(latest_message)>0 else {}
                    chat_obj["latest_message"] = handle_mongoengine_json(latest_message)
                    if chat_obj.get("latest_message"):
                        chats_list.append(chat_obj)
                # if fetch_num_of_new_msgs:
        chats_list = handle_mongoengine_json_array(chats_list)
        chats_list = sorted(chats_list, key=lambda x: ((x.get("latest_message",{}).get("timestamp",datetime.datetime.min))), reverse = True)
        return chats_list
    
        