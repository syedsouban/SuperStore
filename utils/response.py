from functools import wraps

def create_success_response(message):
    return {"message":message, "success": True}

def create_failure_response(message):
    return {"message":message, "success": False}

def get_default_response():
    return {"message":"Something went wrong","success":False}