from app import app
from flask import session, redirect, url_for, render_template, request, Blueprint
from forms.forms import LoginForm
from utils.session import authorize
from database import chat
from database import message as message_module
from flask import jsonify


bp = Blueprint('chat', __name__, url_prefix='/socket_io')

@bp.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('chat.chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('index.html', form=form)


@bp.route('/chat')
def chat_endpoint():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('chat.index'))
    return render_template('chat.html', name=name, room=room)

@bp.route('/active_chats', methods=['GET', 'POST'])
@authorize
def product_chat(user_id, email):
    #fetch chats as a seller
    db = chat.Get()
    html = "<html>"
    seller_id = user_id
    seller_email = email
    selling_chats = db.get_chats_by_buyer_id_seller_id(user_id, "seller")
    response = {
        "buyer_chats":[],
        "seller_chats":[]
    }
    if selling_chats:
        response["seller_chats"] = selling_chats
    
    buyer_id = user_id
    buyer_email = email
    buying_chats = db.get_chats_by_buyer_id_seller_id(user_id, "buyer")
    if buying_chats:
        response["buyer_chats"] = buying_chats

    return response

@bp.route('fetch_messages')
@authorize
def fetch_messages(user_id,email):
    db = chat.Get()
    payload = request.args
    chat_id = payload.get("chat_id")
    timestamp = payload.get("last_timestamp")
    print(str(timestamp))
    db = message_module.Get() 
    messages = db.get_messages_by_chat_id_before(chat_id, timestamp)
    print("messages fetched are",messages," type(messages)=",type(messages))
    return jsonify(messages)


@bp.route('/view_chat')
@authorize
def view_chat(user_id, email):
    payload = request.args
    product_id = payload.get("product_id")
    seller_id = payload.get("seller_id")
    buyer_id = payload.get("buyer_id")
    buyer_email = payload.get("buyer_email")
    seller_email = payload.get("seller_email")
    product_name = payload.get("product_name")
    chat_id = payload.get("chat_id")
    print("chat id recieved in view chat api is: "+chat_id)
    
    if product_id and seller_id and buyer_id:
        room = str(product_id)+"_"+str(seller_id)+"_"+str(buyer_id)
        session['name'] = email
        session['room'] = room
        session_id = session.get("SESSION-ID")
        print("session_id = ",session_id)
        return render_template('chat.html', name=buyer_email, user_id = user_id, room=room, session_id =session_id, buyer_email = buyer_email,seller_email = seller_email, product_name = product_name, chat_id = chat_id)
    else:
        return "Buyer/Seller/Product id missing"
        
