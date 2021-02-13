from flask import session, request
from flask_socketio import join_room, leave_room, emit
from app import socketio
from utils.session import get_active_session_by_id
import json
from models.message import Messages
import logging
from database import message as message_module
import datetime
from utils._json import handle_mongoengine_json


@socketio.on('connect')
def connect():
    print("A client got connected!")
    # session_id = request.args.get('SESSION-ID')
    # print("SESSION-ID = ",session_id)
    # try:
    #     user_session = get_active_session_by_id(session_id)
    #     print(str(user_session))
    #     if not user_session:
    #         return False
    #     else:
    #         return True

@socketio.on('disconnect')
def disconnect():
    print("A client got disconnected!")
    # session.pop("last_msg_timestamp")
    # print("session after disconnect = "+str(session))

#initialize a one-to-one chat
@socketio.on('init_chat', namespace = '/socket_io')
def init_chat(message):
    chat_id = message.get("chat_id")
    print("chat_id from init_chat is: "+chat_id)
    join_room(chat_id)


# client should send an array of 
@socketio.on('joined', namespace='/socket_io')
def joined(message):
    print("message object is: "+json.dumps(message))
    chat_id = message.get("chat_id")
    db = message_module.Get() 
    messages = db.get_messages_by_chat_id(chat_id)
    all_messages_str = ""
    print("trying to fetch lastmsgts using sessionobj = "+str(session))
    last_msg_timestamp = session.get("last_msg_timestamp", 0)
    print("last_message_timestamp = "+str(last_msg_timestamp))
    for msg in messages:
        print("new message timestamp = "+str(msg.get("timestamp")))
        if last_msg_timestamp < msg.get("timestamp"):
            all_messages_str += msg.get("author_email")+":"+msg.get("message")+"\n"
            session["last_msg_timestamp"] = int(str(msg.get("timestamp")))
            print("session object is: "+str(session))
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'message': session.get('name') + ' has entered the room.',"messages":all_messages_str}, room=room)


@socketio.on('text', namespace='/socket_io')
def text(message):
    print("Message object sent is: ",json.dumps(message))
    chat_id = message.get("chat_id")
    message_obj = Messages(**message).save()
    
    if message_obj:
        # print(message_obj.to_json())
        message_json = json.dumps(handle_mongoengine_json(message_obj.to_json()))
        # print("message_json = "+json.dumps(message_json))
        logging.info("Message sent successfully!!!")    
        # message_json = json.dumps({'message': message.get("message"), "author_id": message.get("author_id")})
        
    emit('message', message_json, room=chat_id)


@socketio.on('left', namespace='/socket_io')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'message': session.get('name') + ' has left the room.'}, room=room)

