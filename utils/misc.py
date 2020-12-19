from datetime import datetime
from utils.time import get_time_after
from mongoengine.errors import DoesNotExist
from utils._json import handle_mongoengine_response

def post_process(function_to_decorate):
    def inner(*args, **kw):
        # Calling your function
        output = function_to_decorate(*args, **kw)
        # Below this line you can do post processing
        return handle_mongoengine_response(output)
    return inner

def dict_to_obj(model_class, d):
    if isinstance(d, (list, tuple)):
        return map(dict_to_obj, d)
    elif not isinstance(d, dict):
        return d
    return model_class(dict((k, dict_to_obj(model_class, d[k])) for k in d))


def get_or_none(queryset, *args, **kwargs):
    try:
        return queryset.get(*args, **kwargs)
    except DoesNotExist:
        return None

def append_to_keys(in_dict,suffix):
    out_dict = {}
    for field in in_dict:
        out_dict[suffix+field] = in_dict[field]
    return out_dict

def get_update_dict(in_dict):
    return append_to_keys(in_dict,'set__')

def create_who_columns(email,payload):
    payload["created_by"] = email
    payload["created_date"] = datetime.now()
    payload["updated_by"] = email
    payload["updated_date"] = datetime.now()
    payload["is_active"] = True
    return payload

def create_fields_for_deletion(email):
    document = {}
    document["is_active"] = False
    document["updated_by"] = email
    document["updated_date"] = datetime.now()
    document["expireAt"] = get_time_after(minutes=2)
    return document