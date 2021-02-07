from app import app
from flask import session, redirect, url_for, render_template, request, Blueprint
from forms.forms import LoginForm
from utils.session import authorize
from database import chat

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

@bp.route('/active_chats')
@authorize
def product_chat(user_id, email):
    #fetch chats as a seller
    db = chat.Get()
    html = "<html>"
    seller_id = user_id
    seller_email = email
    selling_chats = db.get_chats_by_buyer_id_seller_id(user_id, "seller")
    if selling_chats:
        html+="<h1>Seller chats</h1>"
        for chat_obj in selling_chats:
            product_id = chat_obj.get("product_id")
            product_name = chat_obj.get("product_english_name")
            buyer_id = chat_obj.get("buyer_id")
            buyer_email  = chat_obj.get("buyer_email")
            html+="<a href='view_chat?seller_id=%s&buyer_id=%s&product_id=%s'>"%(seller_id,buyer_id,product_id)+product_name+" "+" Seller email: "+seller_email+" Buyer email: "+buyer_email+"</a><br>"
    else:
        html+="No Seller chats<br>"
    #fetch chats as a buyer
    buyer_id = user_id
    buyer_email = email
    buying_chats = db.get_chats_by_buyer_id_seller_id(user_id, "buyer")
    if buying_chats:
        html+="<h1>Buyer chats</h1>"    
        for chat_obj in buying_chats:
            product_id = chat_obj.get("product_id")
            product_name = chat_obj.get("product_english_name")
            seller_id = chat_obj.get("seller_id")
            seller_email  = chat_obj.get("seller_email")
            html+="<a href='view_chat?seller_id=%s&buyer_id=%s&product_id=%s'>"%(seller_id,buyer_id,product_id)+product_name+" "+" Seller email: "+seller_email+" Buyer email: "+buyer_email+"</a><br>"
    else:
        html+="No Buyer chats"
    html+="</html>"
    return html

@bp.route('/view_chat')
@authorize
def view_chat(user_id, email):
    payload = request.args
    product_id = payload.get("product_id")
    seller_id = payload.get("seller_id")
    buyer_id = payload.get("buyer_id")
    if product_id and seller_id and buyer_id:
        room = str(product_id)+"_"+str(seller_id)+"_"+str(buyer_id)
        session['name'] = email
        session['room'] = room
        return render_template('chat.html', name=email, room=room)
    else:
        return "Buyer/Seller/Product id missing"
        
