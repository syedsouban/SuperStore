import datetime
import json

def handle_mongoengine_response(response):
    if type(response) == list:
        return handle_mongoengine_json_array(response)
    elif type(response) == dict:
        return handle_mongoengine_json(response)
    else:
        return response

def handle_mongoengine_json_array(input_json:list):
    for i in range(len(input_json)):
        input_json[i] = handle_mongoengine_json(input_json[i])
    return input_json

def handle_mongoengine_json(input_json:dict):
    for key in input_json:
        value = input_json[key]
        if type(value) == dict and any(inner_key.startswith("$") for inner_key in value):
            if "date" in key:
                inner_value = value[list(value.keys())[0]]/1000
                date_field_value = datetime.datetime.fromtimestamp(inner_value).strftime('%Y-%m-%d %H:%M:%S.%f')
                input_json[key] = date_field_value
            else:
                input_json[key] = value[list(value.keys())[0]]
    return input_json