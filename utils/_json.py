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

print(json.dumps(handle_mongoengine_json_array([


{
        "FAQs_arabic": [],
        "FAQs_english": [],
        "_id": {
            "$oid": "5fdd0e31cd2a16bb2926e224"
        },
        "arabic_description": "فطيرة تفاح",
        "arabic_name": "فطيرة تفاح2",
        "category_id": {
            "$oid": "5fdd0deacd2a16bb2926e223"
        },
        "created_by": "syedsoubanw97@gmail.com",
        "created_date": {
            "$date": 1608342409353
        },
        "discount": 12.0,
        "english_description": "description goes here",
        "english_name": "iPad Pro",
        "image_url": "http://s3.blabla.com/121323123",
        "is_active": True,
        "price": 1200.0,
        "seller_id": {
            "$oid": "5fcc8d04486142946595a0c3"
        },
        "status": "edited",
        "tags": [
            "Tablets",
            "Electronics",
            "Smartphones",
            "Gadgets",
            "Office"
        ],
        "updated_by": "syedsoubanw97@gmail.com",
        "updated_date": {
            "$date": 1608342409353
        }
    }
]
)))