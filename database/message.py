from mongoengine.base.fields import ObjectIdField
from utils._json import handle_mongoengine_json_array
from models.message import Messages
from bson.objectid import ObjectId
import logging
import json
from datetime import datetime
from mongoengine.queryset.visitor import Q

class Get:
    def __init__(self):
        pass
    def get_messages_by_chat_id(self, chat_id):
        messages = Messages.objects(chat_id=ObjectId(chat_id)).to_json()
        logging.info("messages fetched from db are: "+json.dumps(messages))
        return handle_mongoengine_json_array(messages)
    
    def get_messages_by_chat_id_before(self, chat_id, timestamp):
        timestamp = datetime.min if not timestamp else datetime.fromtimestamp(int(timestamp)/1000)
        messages = Messages.objects.filter(Q(chat_id=ObjectId(chat_id))&Q(timestamp__gte=timestamp)).to_json()
        logging.info("messages fetched from db are: "+json.dumps(messages))
        return handle_mongoengine_json_array(messages)     
    