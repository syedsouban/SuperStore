import datetime
import json
import logging
from bson import ObjectId

def handle_mongoengine_response(response):
    if type(response) == list:
        return handle_mongoengine_json_array(response)
    elif type(response) == dict:
        return handle_mongoengine_json(response)
    else:
        return response

def handle_mongoengine_json_array(input_json:list):
    if not input_json:
        logging.info("Input json array is empty")
        return {}

    elif type(input_json) == str and is_json(input_json):
        input_json = json.loads(input_json)

    elif type(input_json)!=list:
        logging.info("Input json array = %s, which is not a list or a valid json array string"%str(input_json))
        return {}
    for i in range(len(input_json)):
        input_json[i] = handle_mongoengine_json(input_json[i])
    return input_json

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True
# Message object sent is:  {"message": "heyyy", "chat_id": "60218c01b8209b2691e206c0", "author_id": "5fce1707166d39ecf9406352", "timestamp": "2021-02-13 14:28:06.004731Z"}
def handle_mongoengine_json(input_json:dict):
    if not input_json:
        logging.info("Input json is empty")
        return {}
    elif type(input_json) == str and is_json(input_json):
        input_json = json.loads(input_json)
    elif type(input_json)!=dict:
        logging.info("Input json = %s, which is not a dict or a valid json string"%str(input_json))
        return {}
    for key in input_json:
        value = input_json[key]
        if type(value) == ObjectId:
            input_json[key] = str(value)
        if type(value) == dict and any(inner_key.startswith("$") for inner_key in value):
            if "$date" in value.keys():
                inner_value = value[list(value.keys())[0]]/1000
                date_field_value = datetime.datetime.fromtimestamp(inner_value).strftime('%Y-%m-%d %H:%M:%S.%f')
                input_json[key] = date_field_value
                # print()
            else:
                input_json[key] = value[list(value.keys())[0]]
    return input_json

handle_mongoengine_json({"_id": {"$oid": "6027df273ac6c833d3188d51"}, "chat_id": {"$oid": "60218c01b8209b2691e206c0"}, "message": "hhh", "author_id": {"$oid": "5fce1707166d39ecf9406352"}, "timestamp": {"$date": 1613225767653}})