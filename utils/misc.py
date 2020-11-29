from mongoengine.errors import DoesNotExist


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
