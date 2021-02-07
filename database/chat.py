from utils._json import handle_mongoengine_json_array
from models.chat import Chats
from bson.objectid import ObjectId
from utils._json import is_json
import json

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

    def get_chats_by_buyer_id_seller_id(self, user_id, user_type):
        
        chats = Chats.objects(__raw__ = {user_type+"_id": ObjectId(user_id)})
        antonym_user_type = self.get_user_antonyms(user_type)
        
        chats_list = []
        for i in range(len(chats)):
            product_obj = chats[i].product_id.fetch()
            if is_json(chats[i].to_json()):
                user_obj = self.get_user_field(chats[0], antonym_user_type, "id").fetch()
                chats_list.append(json.loads(chats[i].to_json()))
                chats_list[i].update({"product_english_name":product_obj.english_name, antonym_user_type+"_email":user_obj.email})
            
        return handle_mongoengine_json_array(chats_list)
    
        